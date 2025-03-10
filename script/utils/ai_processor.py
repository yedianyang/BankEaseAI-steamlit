from openai import OpenAI
import json
import os
import streamlit as st

class AIProcessor:
    """
    AI处理器，负责调用不同的AI模型处理文本
    支持的模型：GPT-4o-mini, GPT-4o, DeepSeek, Claude-3
    """
    def __init__(self):
        """
        初始化AI处理器
        :param config_path: 配置文件路径
        """
        #self.config = self._load_config(config_path)
        self.clients = self._initialize_clients()
        
    def _load_config(self, config_path):
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"{config_path} does not exist.")
        with open(config_path, 'r') as file:
            return json.load(file)
    
    def _initialize_clients(self):
        """初始化各个AI客户端"""
        clients = {}
        try:
            # OpenAI客户端
            if hasattr(st.session_state, 'api_key') and st.session_state.api_key:
                clients['openai'] = OpenAI(api_key=st.session_state.api_key)
            else:
                print("Warning: OpenAI API key not found in session state")
            
            #clients['openai'] = OpenAI(api_key=self.config['openai_api_key'])
            # DeepSeek客户端
            # clients['deepseek'] = OpenAI(
            #     api_key=self.config['deepseek_api_key'],
            #     base_url="https://api.deepseek.com"
            # )
            # # Anthropic客户端
            # if 'anthropic_api_key' in self.config:
            #     clients['anthropic'] = anthropic.Anthropic(
            #         api_key=self.config['anthropic_api_key']
            #     )
        except Exception as e:
            print(f"无法访问 AI 服务器: {e}，检查API或网络")
            st.error(f"无法访问 AI 服务器: {e}，检查API或网络")

        return clients

    # def count_tokens(self, text):
    #     """计算文本的token数量"""
    #     try:
    #         encoding = tiktoken.get_encoding("cl100k_base")
    #         return len(encoding.encode(text))
    #     except Exception as e:
    #         print(f"Error counting tokens: {e}")
    #         return 0

    def process_text(self,file_name, clean_lines, model="gpt-4o", temperature=0.3):
        """
        处理文本，根据指定的模型调用相应的API
        :param text: 要处理的文本
        :param model: 使用的模型名称
        :param temperature: 温度参数
        :return: 处理结果
        """
        system_prompt = """你是一个专业的银行账单分析助手。你的任务是：
            1. 准确识别和提取银行账单中的交易记录
            2. 正确分类每笔交易（收入/支出）
            3. 理解交易描述并进行合适的分类
            4. 确保金额和日期的准确性
            5. 遵循指定的输出格式
            请保持专业、准确，并确保不遗漏任何交易记录。"""

        user_prompt = f"""
        请仔细分析以下银行账单文本，提取所有交易记录并按照指定格式输出。

        重要说明：
        1. 请从文件名 "{file_name}" 中提取年份信息。
        2. 所有交易记录必须使用该年份，不要使用其他年份。
        3. 必须处理所有交易记录，绝对不能遗漏任何一条！
        4. 如果内容太长，请确保处理完所有内容再返回！
        5. 交易记录中即使内容相似，也必须逐条完整保留，不能合并或省略。每条记录可通过余额变化等细节进行区分。


        文本内容：
        {clean_lines}

        输出要求：
        1. 格式：日期 | 类型 | 金额 | 一级分类 | 二级分类 | 账户1 | 账户2 | 备注 | 货币 | 标签
        2. 每行一条交易记录
        3. 所有字段用竖线符"|"分隔
        4. 无内容的栏目保持留空
        4. 保留Description字段到备注列中
        5. 从上下文与交易记录的备注中获取对应的银行账户后四位
        6. 不要遗漏任何一条交易信息

        处理规则：
        1. 账户信息：
        - 在账户1和账户2字段中包含账户最后四位数字，用括号括起。
        - 账户格式示例：Chase Checking(1234)。
        
        2. 金额处理：
        - ***保持原始金额的正负值。不要作任何修改***
        - 金额必须包含小数点和两位小数。
        
        3. 日期格式：
        - 必须使用从文件名中提取的年份。
        - 格式：YYYY-MM-DD。
        - 示例：如果文件名中年份是2022，则日期应为2022-01-15。
        
        4. 注意！！！分类规则：
        - 类型栏可填入[转账, 收入, 支出]，金额为负值标记为支出，金额为正，或"+"标记为收入。***转账则标记为转账。***。
        - ***若类型栏为转账，则一级分类与二级分类留空。金额为正时当前账户信息填入[账户2]栏中，金额为负时当前账户信息填入[账户1]栏中***
        - 若类型栏为"支出"，一级分类交易类型选项为 ["水电", "银行服务", "转账", "提现", "出行", "家居", "付款", "住宿", "珠宝", "外汇", "银行转账", "汇款费", "ATM 取款", "其他", "押金", "电汇费", "现金支取", "日用品", "杂货", "手机支付", "杂项", "P2P", "零售", "软件服务", "电子支付", "房贷", "财务费用", "转账支出", "餐饮", "购物", "服饰", "日用", "数码", "美妆", "护肤", "应用软件", "住房", "交通", "娱乐", "医疗", "通讯", "汽车", "学习", "办公", "运动", "社交", "人情", "育儿", "宠物", "旅行", "度假", "烟酒", "彩票", "健康", "费用", "现金", "际汇款手续费", "国内汇款手续费", "电汇手续费", "账单支付", "账单"]
        - 若为网络订阅内容，则标注为：订阅，二级分类填入具体公司名称
        - 若类型栏为"收入"，一级分类交易类型选项为 ["工资", "奖金", "加班", "福利", "公积金", "红包", "兼职", "副业", "退税", "投资", "意外收入", "其他", "收入", "餐饮", "现金", "汇款", "利息", "转账", "退款", "银行转账", "利息收入", "汇款收入", "ATM 存款", "购物退款", "支付"] 
        - 根据交易描述推断一级分类，二级分类可留空。
        - 还款统一标记为信用卡还款。
        - 特别注意Zelle的支出，请将其标注为支出，勿将其视为转账或将Zelle填入账户1或账户2。
        
        5. 交易独立性处理：
        - 即使交易内容相似，必须完整保留每条记录。
        - 可通过余额变化（最后一列数字）来识别和区分每条交易的独立性。
        - 不要省略任何记录，即使内容重复。
        
        6. 其他要求：
        - 根据对账单银行标注货币：若为CHASE/BOFA/AMEX等美国的银行，标注为USD；若为中国的银行，则标注为CNY。
        - 根据交易描述推断标签。

        重要提醒：
        - 必须处理所有交易记录，绝对不能遗漏！
        - 如果内容太长，请确保处理完所有内容再返回！
        - 所有日期必须使用从文件名中提取的年份！
        """

        try:
            # if model.lower() == "gpt-4o-mini":
            #     return self._process_with_gpt4omini(system_prompt, user_prompt, temperature)
            if model.lower() == "gpt-4o":
                return self._process_with_gpt4o(system_prompt, user_prompt, temperature)
            # elif model.lower() == "deepseek-v3":
            #     return self._process_with_deepseek(system_prompt, user_prompt, temperature)
            # elif model.lower() == "claude-3":
            #     return self._process_with_claude()
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            print(f"Error processing text with {model}: {e}")
            return None

    # def _process_with_gpt4omini(self, system_prompt, user_prompt, temperature):
    #     """使用GPT-4o-mini处理文本"""
    #     print(f"使用GPT-4o-mini处理文本")
    #     try:
    #         response = self.clients['openai'].chat.completions.create(
    #             messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": user_prompt}
    #             ],
    #             model="gpt-4o-mini",
    #             temperature=temperature
    #         )
    #         return response.choices[0].message.content.strip()
    #     except Exception as e:
    #         print(f"Error with GPT-4o-mini: {e}")
    #         return None

    def _process_with_gpt4o(self, system_prompt, user_prompt, temperature):
        """使用GPT-4o处理文本"""
        print(f"使用GPT-4o处理文本")
        try:
            response = self.clients['openai'].chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o",
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error with GPT-4o: {e}")
            return None

    # def _process_with_deepseek(self, system_prompt, user_prompt, temperature):
    #     """使用DeepSeek处理文本"""
    #     print(f"使用DeepSeek-V3处理文本")
    #     try:
    #         response = self.clients['deepseek'].chat.completions.create(
    #             model="deepseek-chat",
    #             messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": user_prompt}
    #             ],
    #             temperature=temperature
    #         )
    #         return response.choices[0].message.content.strip()
    #     except Exception as e:
    #         print(f"Error with DeepSeek: {e}")
    #         return None

    # def _process_with_claude(self,system_prompt, user_prompt):
    #     """使用Claude-3处理文本"""
    #     print(f"使用Claude-3处理文本")
    #     try:
    #         if 'anthropic' not in self.clients:
    #             raise ValueError("Claude API key not configured")
            
    #         prompt_tokens = self.count_tokens(user_prompt)
    #         if prompt_tokens > 100000:
    #             raise ValueError("Text exceeds Claude's context window limit")

    #         response = self.clients['anthropic'].messages.create(
    #             model="claude-3-sonnet-20240229",
    #             max_tokens=4096,
    #             system = system_prompt,
    #             messages=[{
    #                 "role": "user",
    #                 "content": user_prompt
    #             }]
    #         )
    #         return response.content[0].text
    #     except Exception as e:
    #         print(f"Error with Claude-3: {e}")
    #         return None
