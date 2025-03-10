import pdfplumber
import re

def extract_text_from_pdf(file_path, settings=None):
    """从 PDF 文件中提取文本内容
    
    Args:
        file_path: PDF 文件路径
        settings: 文本提取参数字典
    """
    extracted_text = ""
    
    default_settings = {
        # 水平和垂直文本合并的容差值
        'x_tolerance': 1,     # 减小水平容差，避免错误合并相邻列
        'y_tolerance': 3,     # 保持垂直容差，以正确识别行间距
        
        # 文本流参数
        'use_text_flow': False,  # 关闭文本流模式，因为账单有固定的列结构
        'horizontal_ltr': True,   # 保持从左到右的阅读顺序
        'vertical_ttb': True,     # 保持从上到下的阅读顺序
        
        # 文本处理参数
        'keep_blank_chars': True,  # 保留空白字符，避免丢失格式
        'strip_text': False,       # 不去除首尾空白，保持原始格式
        
        # 表格参数
        'snap_tolerance': 3,       # 表格对齐容差
        'join_tolerance': 3,       # 表格单元格合并容差
        'edge_min_length': 3,      # 最小边缘长度
        'min_words_vertical': 3    # 垂直文本最小字数
    }
    
    # 如果提供了自定义设置，更新默认值
    if settings:
        default_settings.update(settings)
    
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"\n总页数: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages, 1):
                print(f"\n处理第 {i} 页...")
                
                # 使用设置参数提取文本
                page_text = page.extract_text(**default_settings) or ""
                print(f"提取到 {len(page_text)} 个字符")
                
                # 提取表格
                tables = page.extract_tables()
                print(f"发现 {len(tables)} 个表格")
                
                # 合并页面文本
                extracted_text += page_text + "\n"
                
                # 处理表格内容
                for table in tables:
                    for row in table:
                        # 过滤掉空值并合并行数据
                        row_text = ', '.join(str(cell).strip() for cell in row if cell is not None)
                        if row_text:
                            extracted_text += row_text + '\n'
                
    except Exception as e:
        print(f"处理 PDF 时出错: {str(e)}")
        raise
        
    return extracted_text

def replace_transaction_detail_markers(text):
    '''处理CHASE SAVING 和 CHASE CHECKING 中交易明细标记'''

    """替换文本中的 *end*transacXtion detail 标记为其中包含的数字"""
    # 找到所有匹配的模式
    matches = re.finditer(r'\*end\*transac(\d)tion detail', text.lower())
    
    # 创建一个列表存储位置和数字
    replacements = [(match.start(), match.end(), match.group(1)) for match in matches]
    
    # 从后向前替换每个匹配项
    for start, end, digit in reversed(replacements):
        text = text[:start] + digit + text[end:]
    
    return text

def clean_bank_statement_text(text):
    """根据银行类型清理账单文本"""
    lines = text.split('\n')
    # 检测银行类型
    bank_type = "UNKNOWN"
    account_type = "UNKNOWN"
    
    if "BANK OF AMERICA" in text.upper():
        bank_type = "BOFA"
        if "SAVINGS" in text.upper():
            account_type = "SAVINGS" 
        elif "CHECKING" in text.upper():
            account_type = "CHECKING"
        elif "CREDIT CARD" in text.upper():
            account_type = "CREDITCARD"

    elif "CHASE.COM" in text.upper():
        bank_type = "CHASE"
        if "CREDIT CARD" in text.upper():
            account_type = "CREDITCARD"
        elif "CHASE SAVINGS" in text.upper():
            account_type = "SAVINGS"
        elif "CHASE TOTAL CHECKING" in text.upper():
            account_type = "CHECKING"


    elif "AMERICAN EXPRESS" in text.upper():
        bank_type = "AMEX"
        if "CREDIT CARD" in text.upper():
            account_type = "CREDITCARD"
        elif "SAVINGS" in text.upper():
            account_type = "SAVINGS"
        elif "CHECKING" in text.upper():
            account_type = "CHECKING"
    
    print(f"\n处理 {bank_type} - {account_type} 类型的账单")

    if bank_type == "CHASE" and account_type != "CREDITCARD":
        cleaned_lines, transaction_count = clean_chase_statement(lines)
    if bank_type == "CHASE" and account_type == "CREDITCARD":
        cleaned_lines, transaction_count = clean_chase_creditcard_statement(lines)
    if bank_type == "BOFA":
        cleaned_lines, transaction_count = clean_bofa_statement(lines)
    if bank_type == "AMEX" and account_type == "CREDITCARD":
        cleaned_lines, transaction_count = clean_amex_creditcard_statement(lines)

    return cleaned_lines, transaction_count, bank_type, account_type

def clean_bofa_statement(lines):
    """处理BOFA账单"""
    cleaned_lines = []
    transaction_count = 0
    
    # 初始化交易明细标记和当前交易变量
    is_transaction_detail = False
    current_transaction = None
    
    # 初始化账户后四位变量
    account_last_four = None

    remove_keywords = [
        "Date",
        "Description",
        "Amount",
        "Beginning balance on",
        "Deposits and other additions",
        "ATM and debit card subtractions",
        "Other subtractions",
        "Service fees",
        "Ending balance on",
        "Total deposits and other additions",
        "Total ATM and debit card subtractions",
        "Total other subtractions",
        "Total service fees"
    ]


    # 遍历每一行文本
    for line in lines:
        # 去除行首尾空白
        line = line.strip()
        if not line:
            continue

        # 提取账户后四位
        if "BANK OF AMERICA ADVANTAGE SAVINGS" in line.upper():
           pass

        if "Account number:" in line:
            # 找到所有4位数字组合
            numbers = re.findall(r'\d{4}', line)
            # 取最后一个4位数字作为账号后四位
            if numbers:
                account_last_four = numbers[-1]    
            print(f"找到账户后四位: {account_last_four}")
            cleaned_lines.append(f"\n=== Bank of America Savings Account({account_last_four}) ===")

        
                
        # 检测是否进入交易明细部分
        if "Deposits and other additions" in line or "ATM and debit card subtractions" in line or "Other subtractions" in line:
            is_transaction_detail = True
            continue
            
        # 检测交易记录部分的结束
        if "Total " in line or "Braille and Large Print Request" in line:
            is_transaction_detail = False
            if current_transaction:
                cleaned_lines.append(current_transaction)
                transaction_count += 1
                current_transaction = None
            continue
            
        # 处理交易记录
        if is_transaction_detail:

            # 匹配日期和金额
            date_match = re.search(r'\d{2}/\d{2}/\d{2}', line)
            amount_match = re.search(r'[-]?\$?\d+,?\d*\.\d{2}', line)
            
            # 如果找到日期和金额，说明是新的交易记录
            if date_match and amount_match:
                if current_transaction:
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                current_transaction = line
            # 如果当前行包含超过2个单词，作为交易描述的补充
            elif current_transaction and len(line.split()) > 3:
                current_transaction += " " + line
            # 如果有未处理的交易记录，添加到结果中
            elif current_transaction:
                cleaned_lines.append(current_transaction)
                transaction_count += 1
                current_transaction = None
    
    # 处理最后一个未完成的交易记录
    if current_transaction:
        cleaned_lines.append(current_transaction)
        transaction_count += 1
    
    print(f"\n共找到 {transaction_count} 条交易记录")
    print(cleaned_lines)
    return cleaned_lines, transaction_count

def clean_chase_statement(lines):

    cleaned_lines = []
    transaction_count = 0
    
    """处理CHASE账单"""
        # 初始化交易明细标记和当前交易变量
    is_transaction_detail = False
    current_transaction = None
    
    # 初始化账户后四位变量
    checking_account_last_four = None
    savings_account_last_four = None


    # 遍历每一行文本
    for line in lines:
        # 去除行首尾空白
        line = line.strip()
        if not line:
            continue

        # 提取支票账户后四位
        if "CHASE TOTAL CHECKING" in line.upper():
            match = re.search(r'(\d{4})\b', line)
            if match:
                checking_account_last_four = match.group(1)
        # 提取储蓄账户后四位
        elif "CHASE SAVINGS" in line.upper():
            match = re.search(r'(\d{4})\b', line)
            if match:
                savings_account_last_four = match.group(1)

        # 检测账户类型并添加账户标记
        if "CHECKING SUMMARY" in line.upper():
            if checking_account_last_four:
                cleaned_lines.append(f"\n=== Chase Checking Account({checking_account_last_four}) ===")
            else:
                cleaned_lines.append(f"\n=== Chase Checking Account ===")
            continue
        elif "SAVINGS SUMMARY" in line.upper():
            if savings_account_last_four:
                cleaned_lines.append(f"\n=== Chase Savings Account({savings_account_last_four}) ===")
            else:
                cleaned_lines.append(f"\n=== Chase Savings Account ===")
            continue

        # 跳过包含 "Beginning Balance" 和 "Ending Balance" 的行
        if "BEGINNING BALANCE" in line.upper() or "ENDING BALANCE" in line.upper():
            continue

        
        # 检查是否遇到停止处理的标记
        if "*start*dre portrait disclosure message area" in line.lower():
            print("遇到 dre portrait disclosure 标记，停止处理")
            break
            

        # 检测是否进入交易明细部分
        if any(detail in line.upper() for detail in ["TRANSACTION DETAIL"]):
            is_transaction_detail = True
            continue
            
        # 处理交易记录
        if is_transaction_detail:
            # 遇到透支标记时停止处理
            if "*start*post overdraft and returned" in line.lower():
                print("遇到 overdraft 标记，停止处理")
                break
            
            # 处理特殊的交易标记
            if "*end*transac" in line.lower():
                line = replace_transaction_detail_markers(line)
            
            # 匹配日期和金额
            date_match = re.search(r'\d{2}/\d{2}', line)
            amount_match = re.search(r'[-]?\$?\d+,?\d*\.\d{2}', line)
            
            # 如果找到日期和金额，说明是新的交易记录
            if date_match and amount_match:
                if current_transaction:
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                    #print(f"找到第 {transaction_count} 条交易: {current_transaction}")
                
                current_transaction = line
            # 如果当前行包含超过2个单词，作为交易描述的补充
            elif current_transaction and len(line.split()) > 2:
                current_transaction += " " + line
            # 如果有未处理的交易记录，添加到结果中
            elif current_transaction:
                cleaned_lines.append(current_transaction)
                transaction_count += 1
                #print(f"找到第 {transaction_count} 条交易: {current_transaction}")
                current_transaction = None
    
    # 处理最后一个未完成的交易记录
    if current_transaction:
        cleaned_lines.append(current_transaction)
        transaction_count += 1
        #print(f"找到第 {transaction_count} 条交易: {current_transaction}")
    
    print(f"\n共找到 {transaction_count} 条交易记录")
    
    return cleaned_lines, transaction_count

def clean_chase_creditcard_statement(lines):
    """处理CHASE信用卡账单"""
    cleaned_lines = []
    transaction_count = 0
    
    # 初始化交易明细标记和当前交易变量
    is_transaction_detail = False
    current_transaction = None
    account_last_four = None

    # 定义需要删除的关键词
    remove_keywords = [
        "Date of",
        "Transaction Merchant Name or Transaction Description",
        "$ Amount",
        "PAYMENTS AND OTHER CREDITS",
        "PURCHASE",
        "FEES CHARGED",
        "ACCOUNT ACTIVITY",
        "ACCOUNT ACTIVITY (CONTINUED)"
    ]

    for line in lines:
        # 去除行首尾空白
        line = line.strip()
        if not line:
            continue

        # 提取账户后四位
        if "ACCOUNT NUMBER:" in line.upper():
            numbers = re.findall(r'\d{4}', line)
            if numbers:
                account_last_four = numbers[-1][-4:]
                cleaned_lines.append(f"\n=== Chase Credit Card({account_last_four}) ===")

            print(f"找到账户后四位: {account_last_four}")
                
        # 检测是否进入交易明细部分
        if "PAYMENTS AND OTHER CREDITS" in line.upper() or "PURCHASE" in line.upper() or "ACCOUNT ACTIVITY  (CONTINUED)" in line.upper():
            is_transaction_detail = True
            continue
            
        # 检测交易记录部分的结束
        if "ACCOUNT SUMMARY" in line.upper() or "IMPORTANT NOTICES" in line.upper() or "PAGE" in line.upper():
            is_transaction_detail = False
            if current_transaction:
                cleaned_lines.append(current_transaction)
                transaction_count += 1
                current_transaction = None
            continue
        
        # Interest Charged
        if "INTEREST CHARGED" in line.upper():
            # 这里需要单独设计一个逻辑，将利息也算入账目中
            pass

        # 处理交易记录
        if is_transaction_detail:
            # 跳过关键词行
            if any(keyword in line.upper() for keyword in remove_keywords):
                continue

            # 匹配日期和金额
            date_match = re.search(r'\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b', line)
            amount_match = re.search(r'[-]?\$?(?:\d{1,3}(?:,\d{3})*)?(?:\.\d{2})', line)
            
            if date_match and amount_match:
                if current_transaction:
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                # 将金额转换为相反数
                amount_str = amount_match.group()
                # 移除$和,符号
                amount_str = amount_str.replace('$', '').replace(',', '')
                # 转换为浮点数并取相反数
                amount = -float(amount_str)
                # 如果金额为正数，添加+号
                amount_str = f"+{amount:.2f}" if amount > 0 else f"{amount:.2f}"
                # 替换原始金额
                line = line[:amount_match.start()] + amount_str + line[amount_match.end():]
                current_transaction = line
                
            # 如果当前行是交易描述的补充
            #elif current_transaction and len(line.split()) > 3:
            #    current_transaction += " " + line
    
    # 处理最后一个未完成的交易记录
    if current_transaction:
        cleaned_lines.append(current_transaction)
        transaction_count += 1
    
    print(f"\n共找到 {transaction_count} 条交易记录")
    return cleaned_lines, transaction_count

def clean_amex_creditcard_statement(lines):
    """处理AMEX信用卡账单"""
    cleaned_lines = []
    transaction_count = 0

    current_transaction = None
    account_last_five = None
    is_transaction_detail = False   

    # 定义需要删除的关键词
    remove_keywords = [
        "DATE",
        "DESCRIPTION",
        "AMOUNT",
        "BEGINNING BALANCE ON",
        "DEPOSITS AND OTHER ADDITIONS",
        "NEW CHARGES SUMMARY",
        "NEW CHARGES",
        "SUMMARY",
        r'CARD\s+ENDING\s+\d+-\d+',
        r'NEW CHARGES\s+$\d+,\d{3}\.\d{2}',
    ]


    for line in lines:
        line = line.strip()
        if not line:
            continue


        if "ACCOUNT ENDING" in line.upper():
            # 只在第一次出现时添加账户后五位信息
            if not any("=== American Express Credit Card(" in existing_line for existing_line in cleaned_lines):
                numbers = re.findall(r'\d{5}', line)
                if numbers:
                    account_last_five = numbers[-1]
                    cleaned_lines.append(f"\n=== American Express Credit Card({account_last_five}) ===")

         # 检测是否进入交易明细部分
        if any(keyword in line.upper() for keyword in ("FEES","TOTAL PAYMENTS AND CREDITS","DETAIL","DETAIL *INDICATES POSTING DATE", "DETAIL CONTINUED")):
            is_transaction_detail = True
            #print(line)
            continue

        if "TO RATE INTEREST RATE" in line.upper():
            is_transaction_detail = True
            #if not any("=== INTEREST(" in existing_line for existing_line in cleaned_lines):
                #cleaned_lines.append(f"\n=== INTEREST({account_last_five}) ===")
            continue
        
        # 检测交易记录部分的结束
        #if is_transaction_detail:
        if any(keyword in line.upper() for keyword in ("ABOUT TRAILING INTEREST", "CONTINUED ON REVERSE", "CONTINUED ON NEXT PAGE")):
            is_transaction_detail = False
            #print(line)
            if current_transaction:
                cleaned_lines.append(current_transaction)
                transaction_count += 1
                current_transaction = None
            continue
        

        # 处理交易记录
        if is_transaction_detail:
            #跳过关键词行
            if any(keyword in line.upper() for keyword in remove_keywords):
                continue

            # 使用灵活的正则匹配日期和金额（支持 MM/DD/YY 或 MM/DD/YYYY 的日期格式，金额支持正负符号）
            date_match = re.search(r'\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b', line)
            amount_match = re.search(r'[-+]?\$?\d+(?:,\d{3})*(?:\.\d{2})', line)

            if date_match and amount_match:

                if current_transaction:
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                  
                # 将金额转换为相反数
                amount_str = amount_match.group()
                # 移除 $ 和 , 符号
                clean_amount_str = amount_str.replace('$', '').replace(',', '')
                # 转换为浮点数，并取相反数
                inverted_amount = -float(clean_amount_str)
                # 如果金额为正数，添加 + 号
                formatted_amount = f"+{inverted_amount:.2f}" if inverted_amount > 0 else f"{inverted_amount:.2f}"
                # 替换原始金额部分
                line = line[:amount_match.start()] + formatted_amount + line[amount_match.end():]
                current_transaction = line
                
                if current_transaction and re.match(r'^(Purchases|Cash Advances)\b', line.strip()):
                        # Reformat a transaction line like: "Purchases 10/18/2023 29.99% (v) $0.00 $0.00"
                        # into the new format: "10/18/2023 | Purchases Interest Rate 29.99% | +/-0.00"
                        pattern = re.compile(
                            r'^(Purchases|Cash Advances)\s+'
                            r'(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s+'
                            r'([-+]?\d+(?:\.\d+)?%)\s+'
                            r'(?:\([^)]+\)\s+)?'
                            r'\$?([\d,]+\.\d{2})\s+'
                            r'\$?([\d,]+\.\d{2})'
                        )
                        match = pattern.match(current_transaction.strip())
                        if match:
                            txn_type = match.group(1)
                            date_str = match.group(2)
                            percent_val = match.group(3)
                            # Use the second monetary value (group 5) for the final amount.
                            raw_amount = match.group(5).replace(',', '')
                            try:
                                amount_value = float(raw_amount)
                            except ValueError:
                                amount_value = 0.00
                            inverted_amount = -amount_value
                            formatted_amount = f"+{inverted_amount:.2f}" if inverted_amount > 0 else f"{inverted_amount:.2f}"
                            current_transaction = f"{date_str}  {txn_type} Interest Rate  {formatted_amount}"

            # 如果当前行包含超过2个单词，作为交易描述的补充
            # elif current_transaction and len(line.split()) > 1:
            #     current_transaction += " " + line
            # else:
            #     if current_transaction:
            #         current_transaction += " " + line
            #     else:
            #         current_transaction = line
        #print(current_transaction)

    if current_transaction:
        cleaned_lines.append(current_transaction)
        transaction_count += 1
        
    print(f"\nAMEX信用卡交易记录数量: {transaction_count}")
    return cleaned_lines, transaction_count