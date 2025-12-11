import streamlit as st
import json
import os
import time

# --- 1. 基础配置 ---
IMAGE_DIR = "images"
DATA_FILE = "data.js"

# 确保图片文件夹存在
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- 2. 核心功能函数 ---

def load_data():
    """读取数据"""
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        try:
            # 去掉 JS 的前缀 "window.projectData = " 和后缀 ";"
            json_str = content.replace("window.projectData = ", "").rstrip(";")
            return json.loads(json_str)
        except:
            return []

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # 存为 JS 格式，方便 HTML 直接读取
        json_str = json.dumps(data, ensure_ascii=False, indent=4)
        f.write(f"window.projectData = {json_str};")

def save_uploaded_file(uploaded_file):
    """保存上传的文件"""
    if uploaded_file is None: return None
    file_path = os.path.join(IMAGE_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# --- 3. 界面 UI 设计 ---

st.set_page_config(page_title="Portfolio Admin", layout="centered")
st.title("🎨 网站内容管理后台")
st.info("在这里上传，你的个人主页会自动更新。")

# 读取现有数据
current_data = load_data()

# --- 左侧边栏：显示清单 ---
st.sidebar.header(f"📦 已发布 ({len(current_data)})")
for i, item in enumerate(current_data):
    st.sidebar.text(f"{i+1}. {item['title']}")

# --- 主区域：上传表单 ---
with st.form("upload_form", clear_on_submit=True):
    st.subheader("📤 上传新作品")
    
    col1, col2 = st.columns(2)
    title = col1.text_input("作品标题", placeholder="例如：龙吟茶礼")
    category = col2.text_input("分类标签", placeholder="例如：AI PACKAGING")
    
    desc = st.text_area("作品描述", height=150, placeholder="描述将以深灰色小字显示在详情页...")
    
    st.markdown("---")
    st.markdown("**📂 资源文件**")
    
    cover_file = st.file_uploader("1. 封面图 (必须，将作为详情页首图)", type=['jpg', 'png', 'jpeg', 'webp'])
    video_file = st.file_uploader("2. 视频 (可选 MP4)", type=['mp4'])
    detail_files = st.file_uploader("3. 更多插图 (可选多张)", type=['jpg', 'png', 'jpeg', 'webp'], accept_multiple_files=True)
    
    submitted = st.form_submit_button("🚀 发布到网站", type="primary")

    if submitted:
        if not title or not cover_file:
            st.error("❌ 标题和封面图是必须的！")
        else:
            # 1. 保存文件
            cover_path = save_uploaded_file(cover_file)
            video_path = save_uploaded_file(video_file) if video_file else ""
            
            detail_paths = []
            if detail_files:
                for f in detail_files:
                    path = save_uploaded_file(f)
                    if path: detail_paths.append(path)
            
            # 2. 构建数据对象
            new_project = {
                "id": int(time.time()), # 时间戳ID
                "title": title,
                "category": category,
                "desc": desc,
                "cover": cover_path,
                "video": video_path,
                "images": detail_paths
            }
            
            # 3. 插入到最前面
            current_data.insert(0, new_project)
            save_data(current_data)
            
            st.success("✅ 发布成功！请刷新你的主页查看。")
            time.sleep(1)
            st.rerun()

# --- 底部：删除功能 (显眼版) ---
st.markdown("---")
st.subheader("🗑 管理已发布作品")

col_del_1, col_del_2 = st.columns([3, 1])

with col_del_1:
    # 删除选择框
    project_to_delete = st.selectbox(
        "选择要删除的作品", 
        [item['title'] for item in current_data], 
        index=None,
        placeholder="请选择..."
    )

with col_del_2:
    st.write("") # 占位，为了对齐
    st.write("")
    # 删除按钮
    if st.button("确认删除"):
        if project_to_delete:
            # 过滤掉选中的作品
            new_list = [p for p in current_data if p['title'] != project_to_delete]
            save_data(new_list)
            st.toast(f"已删除：{project_to_delete}")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("请先在左侧选择一个作品")
