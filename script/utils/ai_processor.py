from openai import OpenAI
import json
import os
import streamlit as st
import time
import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum

# 配置日志
import os
import logging

# 根据环境设置日志级别
if os.environ.get('STREAMLIT_ENV') == 'production':
    logging.basicConfig(level=logging.WARNING)  # 生产环境只显示警告和错误
else:
    logging.basicConfig(level=logging.INFO)     # 开发环境显示详细信息

logger = logging.getLogger(__name__)

class AIErrorType(Enum):
    """AI错误类型枚举"""
    API_KEY_MISSING = "api_key_missing"
    API_KEY_INVALID = "api_key_invalid"
    NETWORK_ERROR = "network_error"
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    MODEL_UNAVAILABLE = "model_unavailable"
    CONTENT_TOO_LONG = "content_too_long"
    UNKNOWN_ERROR = "unknown_error"

class AIProcessorError(Exception):
    """AI处理器自定义异常"""
    def __init__(self, error_type: AIErrorType, message: str, original_error: Optional[Exception] = None):
        self.error_type = error_type
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class AIProcessor:
    """
    AI处理器，负责调用不同的AI模型处理文本
    支持的模型：GPT-4o-mini, GPT-4o, DeepSeek, Claude-3
    """
    def __init__(self):
        """
        初始化AI处理器
        """
        self.clients = self._initialize_clients()
        self.max_retries = 3
        self.retry_delay = 1  # 秒
        
    def _initialize_clients(self) -> Dict[str, Any]:
        """初始化各个AI客户端"""
        clients = {}
        
        try:
            # OpenAI客户端
            api_key = self._get_openai_api_key()
            if api_key:
                clients['openai'] = OpenAI(api_key=api_key)
                logger.info("OpenAI客户端初始化成功")
            else:
                logger.warning("OpenAI API key not found")
                
        except Exception as e:
            logger.error(f"初始化AI客户端失败: {e}")
            st.error(f"AI服务初始化失败: {str(e)}")
            
        return clients
    
    def _get_openai_api_key(self) -> Optional[str]:
        """获取OpenAI API密钥"""
        try:
            # 优先从session_state获取
            if hasattr(st.session_state, 'api_key') and st.session_state.api_key:
                return st.session_state.api_key
            
            # 从secrets获取
            if hasattr(st, 'secrets') and st.secrets.get('openai_api_key'):
                return st.secrets.get('openai_api_key')
                
            # 从环境变量获取
            return os.getenv('OPENAI_API_KEY')
            
        except Exception as e:
            logger.error(f"获取API密钥失败: {e}")
            return None

    # def count_tokens(self, text):
    #     """计算文本的token数量"""
    #     try:
    #         encoding = tiktoken.get_encoding("cl100k_base")
    #         return len(encoding.encode(text))
    #     except Exception as e:
    #         print(f"Error counting tokens: {e}")
    #         return 0

    def process_text(self, file_name: str, clean_lines: str, model: str = "gpt-4o", temperature: float = 0.3) -> Optional[str]:
        """
        处理文本，根据指定的模型调用相应的API
        :param file_name: 文件名
        :param clean_lines: 要处理的文本
        :param model: 使用的模型名称
        :param temperature: 温度参数
        :return: 处理结果
        """
        try:
            # 验证输入参数
            self._validate_inputs(file_name, clean_lines, model, temperature)
            
            # 检查内容长度
            if len(clean_lines) > 100000:  # 约100k字符
                raise AIProcessorError(
                    AIErrorType.CONTENT_TOO_LONG,
                    "内容过长，请尝试分割处理"
                )
            
            # 构建提示词
            system_prompt, user_prompt = self._build_prompts(file_name, clean_lines)
            
            # 根据模型选择处理方法
            if model.lower() == "gpt-4o":
                return self._process_with_retry(
                    self._process_with_gpt4o,
                    system_prompt, user_prompt, temperature
                )
            else:
                raise AIProcessorError(
                    AIErrorType.MODEL_UNAVAILABLE,
                    f"不支持的模型: {model}"
                )
                
        except AIProcessorError as e:
            self._handle_ai_error(e)
            return None
        except Exception as e:
            logger.error(f"处理文本时发生未知错误: {e}")
            st.error(f"处理失败: {str(e)}")
            return None
    
    def _validate_inputs(self, file_name: str, clean_lines: str, model: str, temperature: float):
        """验证输入参数"""
        if not file_name or not isinstance(file_name, str):
            raise ValueError("文件名不能为空")
        
        if not clean_lines or not isinstance(clean_lines, str):
            raise ValueError("文本内容不能为空")
        
        if not model or not isinstance(model, str):
            raise ValueError("模型名称不能为空")
        
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            raise ValueError("温度参数必须在0-2之间")
    
    def _build_prompts(self, file_name: str, clean_lines: str) -> Tuple[str, str]:
        """构建系统提示词和用户提示词"""
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
        5. 保留Description字段到备注列中
        6. 从上下文与交易记录的备注中获取对应的银行账户后四位
        7. 不要遗漏任何一条交易信息

        处理规则：
        1. 账户信息：在账户1和账户2字段中包含账户最后四位数字，用括号括起。
        2. 金额处理：保持原始金额的正负值，金额必须包含小数点和两位小数。
        3. 日期格式：必须使用从文件名中提取的年份，格式：YYYY-MM-DD。
        4. 分类规则：类型栏可填入[转账, 收入, 支出]，根据金额正负和交易描述判断。
        5. 交易独立性：即使交易内容相似，必须完整保留每条记录。
        6. 货币标注：根据银行类型标注USD或CNY。

        重要提醒：
        - 必须处理所有交易记录，绝对不能遗漏！
        - 所有日期必须使用从文件名中提取的年份！
        """
        
        return system_prompt, user_prompt
    
    def _process_with_retry(self, process_func, *args, **kwargs) -> Optional[str]:
        """带重试机制的处理方法"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"尝试第 {attempt + 1} 次处理")
                result = process_func(*args, **kwargs)
                if result:
                    logger.info("处理成功")
                    return result
                    
            except AIProcessorError as e:
                last_error = e
                if e.error_type in [AIErrorType.RATE_LIMIT, AIErrorType.NETWORK_ERROR]:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # 指数退避
                        logger.warning(f"遇到 {e.error_type.value} 错误，{wait_time}秒后重试")
                        time.sleep(wait_time)
                        continue
                break
                
            except Exception as e:
                last_error = AIProcessorError(AIErrorType.UNKNOWN_ERROR, str(e), e)
                break
        
        if last_error:
            self._handle_ai_error(last_error)
        
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

    def _process_with_gpt4o(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """使用GPT-4o处理文本"""
        logger.info("使用GPT-4o处理文本")
        
        # 检查客户端是否可用
        if 'openai' not in self.clients:
            raise AIProcessorError(
                AIErrorType.API_KEY_MISSING,
                "OpenAI客户端未初始化，请检查API密钥配置"
            )
        
        try:
            response = self.clients['openai'].chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o",
                temperature=temperature,
                max_tokens=4000,  # 限制输出长度
                timeout=60  # 设置超时
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise AIProcessorError(
                    AIErrorType.UNKNOWN_ERROR,
                    "AI返回空响应"
                )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # 根据异常类型进行分类
            error_type, message = self._classify_openai_error(e)
            raise AIProcessorError(error_type, message, e)
    
    def _classify_openai_error(self, error: Exception) -> Tuple[AIErrorType, str]:
        """分类OpenAI API错误"""
        error_str = str(error).lower()
        
        if "api key" in error_str or "authentication" in error_str:
            return AIErrorType.API_KEY_INVALID, "API密钥无效，请检查配置"
        
        elif "rate limit" in error_str or "quota" in error_str:
            return AIErrorType.RATE_LIMIT, "API调用频率超限，请稍后重试"
        
        elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
            return AIErrorType.NETWORK_ERROR, "网络连接问题，请检查网络"
        
        elif "model" in error_str and "not found" in error_str:
            return AIErrorType.MODEL_UNAVAILABLE, "模型不可用"
        
        elif "context length" in error_str or "too long" in error_str:
            return AIErrorType.CONTENT_TOO_LONG, "内容过长，请分割处理"
        
        else:
            return AIErrorType.UNKNOWN_ERROR, f"未知错误: {str(error)}"
    
    def _handle_ai_error(self, error: AIProcessorError):
        """处理AI错误，显示用户友好的错误信息"""
        logger.error(f"AI处理错误: {error.error_type.value} - {error.message}")
        
        # 根据错误类型显示不同的用户提示
        if error.error_type == AIErrorType.API_KEY_MISSING:
            st.error("🔑 API密钥未配置，请在设置中配置OpenAI API密钥")
            st.info("💡 您可以在Streamlit Cloud的Secrets中配置API密钥")
            
        elif error.error_type == AIErrorType.API_KEY_INVALID:
            st.error("❌ API密钥无效，请检查密钥是否正确")
            st.info("💡 请确认API密钥格式正确且有效")
            
        elif error.error_type == AIErrorType.RATE_LIMIT:
            st.warning("⏰ API调用频率超限，请稍后重试")
            st.info("💡 建议等待几分钟后再次尝试")
            
        elif error.error_type == AIErrorType.NETWORK_ERROR:
            st.error("🌐 网络连接问题，请检查网络连接")
            st.info("💡 请确认网络连接正常后重试")
            
        elif error.error_type == AIErrorType.MODEL_UNAVAILABLE:
            st.error("🤖 AI模型不可用，请稍后重试")
            st.info("💡 模型可能暂时维护，请稍后再试")
            
        elif error.error_type == AIErrorType.CONTENT_TOO_LONG:
            st.warning("📄 内容过长，请尝试分割处理")
            st.info("💡 建议将PDF内容分成较小的部分处理")
            
        else:
            st.error(f"❌ 处理失败: {error.message}")
            st.info("💡 如问题持续，请联系技术支持")

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
