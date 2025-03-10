import os
import pandas as pd
from utils import extract_text_from_pdf, clean_bank_statement_text, process_batches
from utils.ai_processor import AIProcessor
import json
import streamlit as st

# Import functions from pdf_processor and batch_processor
# Adjust the import paths if your project structure differs
from utils.pdf_processor import extract_text_from_pdf, clean_bank_statement_text
from utils.batch_processor import process_batches, get_batch_status


class BankStatementController:
    """
    业务逻辑控制器，负责整合PDF处理、批次处理、AI分析以及生成iCost格式Excel文件。
    参考模块: main_tk.py, batch_processor.py, pdf_processor.py
    """
    def __init__(self, output_dir="~/Downloads", model="gpt-4o", temperature=0.3, batch_size=150):
        """
        初始化控制器
        :param output_dir: 输出Excel文件的目录
        :param model: 使用的AI模型名称
        :param temperature: AI模型温度参数
        :param batch_size: 批次处理时每批的行数
        """
        self.output_dir = os.path.expanduser(output_dir)
        self.model = model
        self.temperature = temperature
        self.batch_size = batch_size
        # 加载配置文件并初始化AI处理器
        # with open('../script/config.json', 'r') as f:
        #     self.config = json.load(f)
        self.ai_processor = AIProcessor()

    def process_files(self, file, model=None, temperature=0.3, batch_size=150, callback=None):
        """
        处理单个银行账单PDF文件
        :param file: 单个PDF文件
        :param model: 使用的AI模型
        :param temperature: AI模型温度参数
        :param batch_size: 批次处理时每批的行数
        :param callback: 回调函数，用于更新进度
        :return: 处理结果
        """
        try:
            # 提取PDF中的文本
            pdf_text = extract_text_from_pdf(file)
            if not pdf_text or not pdf_text.strip():
                print(f"无法从文件 {file.name} 中提取文本。")
                if callback:
                    callback(
                        filename=file.name,
                        total_transactions=0,
                        bank_type="提取失败",
                        account_type="提取失败"
                    )
                return None


            # 清理文本，获取交易记录行和银行、账户类型
            cleaned_lines, transaction_count, bank_type, account_type = clean_bank_statement_text(pdf_text)
            if transaction_count == 0:
                print(f"在文件 {file.name} 中未找到有效的交易记录。")
                if callback:
                    callback(
                        filename=file.name,
                        total_transactions=0,
                        bank_type=bank_type,
                        account_type=account_type
                    )
                return None

            print(cleaned_lines)

            # 使用批次处理，将清理后的文本分批
            batches = process_batches(cleaned_lines, self.batch_size)
            print(f"分割为 {len(batches)} 个批次")

            # 使用AI处理器处理每个批次
            transaction_data = []
            total_processed_count = 0
            for batch in batches:
                ai_response = self.ai_processor.process_text(
                    file_name=file.name,
                    clean_lines=batch.get_text(),
                    model=model,
                )
                parsed_transactions, parsed_count = self.parse_ai_response(ai_response)
                print(f"Batch {batch.index + 1} AI处理结果: {parsed_transactions}")
                print(f"Batch {batch.index + 1} AI处理总数: {parsed_count}")
                if parsed_transactions:
                    transaction_data.extend(parsed_transactions)
                    total_processed_count += parsed_count

            print(f"所有Batch AI处理结果总数: {total_processed_count}")
            
            # 保存处理结果
            excel_data, output_file = self.save_to_excel(transaction_data, file.name, bank_type)

            # 处理完成后调用回调函数
            if callback:
                callback(
                    filename=file.name,
                    total_transactions=transaction_count,
                    bank_type=bank_type,
                    account_type=account_type,
                    total_processed_count=total_processed_count,
                    output_file=output_file,
                    excel_data=excel_data,
                    error_message=None
                )
            
            return {
                'transaction_count': transaction_count,
                'bank_type': bank_type,
                'account_type': account_type,
                'batches': len(batches),
                'total_processed_count': total_processed_count,
                'output_file': output_file,
                'excel_data': excel_data,
                'error_message': None
            }
            
        except Exception as e:
            print(f"处理文件 {file.name} 时出错: {str(e)}")
            if callback:
                callback(
                    filename=file.name,
                    total_transactions=0,
                    bank_type="处理失败",
                    account_type="处理失败",
                    total_processed_count=0,
                    output_file=None,
                    excel_data=None,
                    error_message=str(e)
                )
            return None
        
        

    def parse_ai_response(self, response_text):
        """
        解析AI响应文本，将每行交易记录分割为10个字段
        :param response_text: AI返回的完整文本
        :return: 交易记录的列表，每条记录为包含10个字段的列表
        """
        transactions = []
        lines = response_text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) == 10:
                transactions.append(parts)
            else:
                print(f"跳过格式不正确的行: {line}")
        print(f"解析出 {len(transactions)} 条交易记录")
        return transactions, len(transactions)

    def save_to_excel(self, transactions, pdf_path, bank_type):
        """
        将交易数据保存到一个Excel文件中，格式符合iCost模板要求
        :param transactions: 交易记录列表
        :param pdf_path: 原始PDF文件路径（用于生成文件名的一部分）
        :param bank_type: 银行类型，用于文件命名
        :return: tuple (DataFrame, str) - (Excel数据对象, 生成的Excel文件路径)
        """
        headers = ["日期", "类型", "金额", "一级分类", "二级分类", "账户1", "账户2", "备注", "货币", "标签"]
        df = pd.DataFrame(transactions, columns=headers)
        
        # 从PDF文件名中提取年份和月份信息，作为文件名的一部分
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{bank_type}-{base_name}-{self.model}-icost.xlsx"
        #output_file_path = os.path.join(self.output_dir, output_filename)
        
        # 写入Excel文件：第一部分为示例模板（空表头），第二部分为实际数据
        #with pd.ExcelWriter(output_file_path, engine="openpyxl") as writer:
            # 写入空模板
        #    pd.DataFrame(columns=headers).to_excel(writer, index=False, sheet_name="iCost Template")
            # 写入数据，数据从第二行开始（下标1）
        #    df.to_excel(writer, index=False, header=False, startrow=1, sheet_name="iCost Template")
        
        return df, output_filename

    def update_settings(self, openai_key=None, deepseek_key=None):
        """更新 API keys 设置"""
        if openai_key:
            self.config['openai_api_key'] = openai_key
        if deepseek_key:
            self.config['deepseek_api_key'] = deepseek_key
            
        # 保存更新后的配置
        with open('script/config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
        return True
