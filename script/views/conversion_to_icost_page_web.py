# views/conversion_to_icost_page_web.py
import streamlit as st
import pandas as pd
import zipfile
import io
import os

class ConversionToiCostPage:
    def __init__(self, controller=None):
        self.controller = controller
        if 'file_data' not in st.session_state:
            st.session_state.file_data = []
        
        # 添加容器的占位符
        self.table_placeholder = None
        self.status_placeholder = None
        self.download_placeholder = None

    def render(self):
        """渲染转换页面"""
        col1, col2 = st.columns([1, 8])
        with col1:
            st.image("./Assets/iCost_icon.png", width=70)
        with col2:
            st.header("iCost模版")
        
        # 在 session_state 中添加一个键来追踪文件上传器的键
        if 'uploader_key' not in st.session_state:
            st.session_state.uploader_key = 0

        st.markdown("---")

        # 模型设置区域
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                model = st.selectbox(
                    "选择模型",
                    options=["GPT-4o"],#,"GPT-4o-mini", "DeepSeek-V3"],
                    help="选择用于处理文件的AI模型-web"
                )
                temperature = 0.3
                batch_size = 150
            with col2:
                # API key 输入框
                api_key = st.text_input(
                    "OpenAI API", 
                    type="password",  # 使用password类型隐藏输入内容
                    help="输入对应模型的API Key",
                    key="api_key_input"
                )
                # 如果输入了API key，保存到session state
                if api_key:
                    st.session_state.api_key = api_key
                
            
        st.write("\n")

        # 文件上传区域
        with st.container():
            # 添加上传区域和清除按钮的列布局
            upload_col, clear_col = st.columns([8, 1])
            
            
            with upload_col:
                uploaded_files = st.file_uploader(
                    "请将PDF银行账单拖入框中，或点击上传按钮(支持多个文件)",
                    type=["pdf"],
                    accept_multiple_files=True,
                    label_visibility="visible",
                    key=f"file_uploader_{st.session_state.uploader_key}"  # 使用动态key
                )
            
            # 获取当前上传的文件名列表
            current_uploaded_filenames = {file.name for file in uploaded_files} if uploaded_files else set()
            
            # 从 session_state.file_data 中移除已经不在上传列表中的文件
            st.session_state.file_data = [
                f for f in st.session_state.file_data 
                if f["文件名"] in current_uploaded_filenames
            ]

            if uploaded_files:
                # 检查是否有新文件需要添加到 file_data
                current_files = {f['文件名'] for f in st.session_state.file_data}
                for file in uploaded_files:
                    if file.name not in current_files:
                        st.session_state.file_data.append({
                            "文件名": file.name,
                            "交易条数": "待处理", 
                            "已处理条数": "待处理",
                            "银行类型": "待处理",
                            "账户类型": "待处理",
                            "需要处理": True,
                            "输出文件": None
                        })
                
                # 创建占位符
                self.table_placeholder = st.empty()
                self.status_placeholder = st.empty()
                
                # 更新文件表格显示
                self.update_file_table()


        # 操作按钮区域
        button_col1, button_col2, button_col3 = st.columns([0.7, 1, 3])  # 调整三列的比例
        
        # 开始处理按钮
        process_button = button_col1.button("开始处理", type="primary")
        
        # 清除按钮
        if button_col2.button("清除所有文件", type="secondary", use_container_width=True):
            # 增加 uploader_key 来强制重新创建上传组件
            st.session_state.uploader_key += 1
            # 清空 session_state 中的文件数据
            st.session_state.file_data = []
            # 重新加载页面
            st.rerun()
        
        # 下载按钮的占位符
        self.download_placeholder = button_col3.empty()

        if process_button:
            if not uploaded_files:
                st.warning("请先上传文件")
                return
            
            if self.controller:
                # 只处理被选中需要处理的文件
                files_to_process = [
                    file for file in uploaded_files 
                    if any(f["文件名"] == file.name and f["需要处理"] 
                          for f in st.session_state.file_data)
                ]
                
                if not files_to_process:
                    st.warning("请选择至少一个需要处理的文件")
                    return

                # 显示进度信息
                status_text = st.empty()
                processed_files = []  # 存储处理完成的文件信息
                
                # 逐个处理文件
                for i, file in enumerate(files_to_process, 1):
                    status_text.text(f"正在处理: {file.name} ({i}/{len(files_to_process)})")
                    
                    try:
                        result = self.controller.process_files(
                            file=file,
                            model=model.lower(),
                            temperature=temperature,
                            batch_size=batch_size,
                            callback=self.update_progress
                        )
                        
                        if result is None:  # 处理失败
                            st.error(f"文件 {file.name} 处理失败，请检查错误信息。")
                            continue
                            
                        # 存储处理成功的文件信息
                        processed_files.append({
                            'filename': file.name,
                            'excel_data': result['excel_data'],
                            'output_file': result['output_file']
                        })
                            
                    except Exception as e:
                        st.toast(f"❌ 处理文件 {file.name} 时发生错误: {str(e)}，请检查API Key或网络连接", icon="🚨")
                        continue
                
                #status_text.text("所有文件处理完成！")
                
                # 如果有成功处理的文件，提供下载选项
                if processed_files:
                    if len(processed_files) > 1:
                        # 多文件：创建ZIP文件在内存中
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for processed_file in processed_files:
                                excel_buffer = io.BytesIO()
                                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                    pd.DataFrame(columns=processed_file['excel_data'].columns).to_excel(
                                        writer, index=False, sheet_name="iCost Template"
                                    )
                                    processed_file['excel_data'].to_excel(
                                        writer, index=False, header=False, 
                                        startrow=1, sheet_name="iCost Template"
                                    )
                                excel_buffer.seek(0)
                                zip_file.writestr(processed_file['output_file'], excel_buffer.getvalue())
                        
                        zip_buffer.seek(0)
                        # 更新下载按钮 - ZIP文件
                        self.download_placeholder.download_button(
                            label="下载ZIP文件",
                            data=zip_buffer,
                            file_name="processed_files.zip",
                            mime="application/zip"
                        )
                    else:
                        # 单文件：直接创建Excel文件在内存中
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            pd.DataFrame(columns=processed_files[0]['excel_data'].columns).to_excel(
                                writer, index=False, sheet_name="iCost Template"
                            )
                            processed_files[0]['excel_data'].to_excel(
                                writer, index=False, header=False, 
                                startrow=1, sheet_name="iCost Template"
                            )
                        excel_buffer.seek(0)
                        # 更新下载按钮 - Excel文件
                        self.download_placeholder.download_button(
                            label="下载Excel文件",
                            data=excel_buffer,
                            file_name=processed_files[0]['output_file'],
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

    def update_file_table(self):
        """更新文件表格显示"""
        if st.session_state.file_data:
            df = pd.DataFrame(st.session_state.file_data)
            self.table_placeholder.dataframe(
                df,
                column_config={
                    "文件名": st.column_config.TextColumn("文件名称"),
                    "交易条数": st.column_config.NumberColumn("交易总数", format="%d"),
                    "已处理条数": st.column_config.NumberColumn("已完成数", format="%d"),
                    "银行类型": st.column_config.TextColumn("所属银行"),
                    "账户类型": st.column_config.TextColumn("账户种类"),
                    "需要处理": st.column_config.CheckboxColumn("是否处理"),
                    "输出文件": st.column_config.TextColumn("输出文件")
                },
                hide_index=True,
                use_container_width=True
            )

    def update_progress(self, filename, total_transactions=None, total_processed_count=None, 
                       bank_type=None, account_type=None, output_file=None, excel_data=None,
                       error_message=None):
        """更新处理进度的回调函数"""
        for item in st.session_state.file_data:
            if item["文件名"] == filename:
                if total_transactions is not None:
                    item["交易条数"] = str(total_transactions)
                if total_processed_count is not None:
                    item["已处理条数"] = str(total_processed_count)
                if bank_type is not None:
                    item["银行类型"] = bank_type
                if account_type is not None:
                    item["账户类型"] = account_type
                if output_file is not None:
                    item["输出文件"] = output_file
                break
        
        # 更新表格显示
        self.update_file_table()
        
        # 如果有错误信息，显示错误提示
        if error_message:
            self.status_placeholder.error(f"❌ 处理文件 {filename} 失败: {error_message}，请检查API Key或网络连接", icon="🚨")
        

