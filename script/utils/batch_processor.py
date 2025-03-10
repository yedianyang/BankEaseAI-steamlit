class Batch:
    """批次数据的封装类"""
    def __init__(self, content, header=None):
        self.header = header          # 批次的标题（账户信息）
        self.content = content        # 批次的内容（交易记录）
        self.length = len(content)    # 批次的交易数量
        self.index = None            # 批次的序号
        self.processed = False       # 处理状态
        self.result = None          # 处理结果
        
    def get_text(self):
        """获取批次的完整文本"""
        text = []
        if self.header:
            text.append(self.header)
        text.extend(self.content)
        return '\n'.join(text)
    
    def __str__(self):
        """字符串表示"""
        return f"Batch {self.index + 1 if self.index is not None else 'N/A'} ({self.length} records)"

def process_batches(cleaned_lines, batch_size):
    """
    将清理后的文本分批处理
    
    Args:
        cleaned_lines: 清理后的文本行列表
        batch_size: 每批处理的行数
        
    Returns:
        batches: Batch对象的列表
    """
    batches = []
    current_header = None
    current_batch = []
    
    for i, line in enumerate(cleaned_lines):
        # 检查是否是新的账户部分标题
        if "=== Chase Checking" in line:
            # 如果存在当前批次，保存它
            if current_batch:
                batch = Batch(current_batch, current_header)
                batch.index = len(batches)
                batches.append(batch)
                current_batch = []
            current_header = line
            continue
            
        # 检查是否是储蓄账户部分
        if "=== Chase Savings" in line:
            # 保存当前批次
            if current_batch:
                batch = Batch(current_batch, current_header)
                batch.index = len(batches)
                batches.append(batch)
                current_batch = []
            # 创建新的储蓄账户批次
            current_header = line
            continue
        
        if "=== Bank of America Savings" in line:
            # 保存当前批次
            if current_batch:
                batch = Batch(current_batch, current_header)
                batch.index = len(batches)
                batches.append(batch)
                current_batch = []
            # 创建新的储蓄账户批次
            current_header = line
            continue

        if "=== Chase Credit Card" in line:
            if current_batch:
                batch = Batch(current_batch, current_header)
                batch.index = len(batches)
                batches.append(batch)
                current_batch = []
            # 创建新的储蓄账户批次
            current_header = line
            continue

        if "=== American Express Credit Card" in line:
            if current_batch:
                batch = Batch(current_batch, current_header)
                batch.index = len(batches)
                batches.append(batch)
                current_batch = []
            # 创建新的储蓄账户批次
            current_header = line
            continue

        # 将行添加到当前批次
        current_batch.append(line)
        
        # 检查批次是否已满或是最后一行
        if len(current_batch) >= batch_size or i == len(cleaned_lines) - 1:
            if current_batch:  # 确保批次不为空
                batch = Batch(current_batch, current_header)
                batch.index = len(batches)
                batches.append(batch)
                current_batch = []
    print(f"分割为 {len(batches)} 个批次")
    
    
    return batches

def merge_batch_results(batches):
    """
    合并所有批次的处理结果
    
    Args:
        batches: 已处理的Batch对象列表
        
    Returns:
        merged_text: 合并后的文本
    """
    merged_results = []
    
    for batch in batches:
        if batch.processed and batch.result:
            merged_results.append(batch.result)
    
    return '\n'.join(merged_results)

def get_batch_status(batches):
    """
    获取批次处理状态的统计信息
    
    Args:
        batches: Batch对象列表
        
    Returns:
        dict: 包含处理状态的字典
    """
    total = len(batches)
    processed = sum(1 for batch in batches if batch.processed)
    successful = sum(1 for batch in batches if batch.processed and batch.result)
    failed = processed - successful
    
    return {
        'total': total,
        'processed': processed,
        'successful': successful,
        'failed': failed,
        'remaining': total - processed
    }