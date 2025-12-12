import streamlit as st
import json
import os
import time

# --- 1. 基础配置 ---
IMAGE_DIR = "images"
DATA_FILE = "data.js"

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

# 读取现有数据
current_data = load_data()

# --- 侧边栏：模式选择 ---
st.sidebar.header("⚙️ 操作面板")
mode = st.sidebar.radio("选择模式", ["➕ 新建作品", "✏️ 编辑已有作品"])

# 初始化表单默认值
default_title = ""
default_category = ""
default_desc = ""
edit_index = -1
old_cover = ""
old_video = ""
old_images = []

# 如果是编辑模式，处理选择逻辑
if mode == "✏️ 编辑已有作品":
    if not current_data:
        st.warning("暂无作品可编辑，请先新建。")
        st.stop()
    
    # 获取作品标题列表供选择
    titles = [item['title'] for item in current_data]
    selected_title = st.sidebar.selectbox("选择要修改的作品", titles)
    
    # 找到对应的数据
    for idx, item in enumerate(current_data):
        if item['title'] == selected_title:
            edit_index = idx
            default_title = item.get('title', '')
            default_category = item.get('category', '')
            default_desc = item.get('desc', '')
            old_cover = item.get('cover', '')
            old_video = item.get('video', '')
            old_images = item.get('images', [])
            break
    
    st.info(f"正在编辑：**{selected_title}**")

# --- 主表单区域 ---
with st.form("project_form", clear_on_submit=False): 
    # 注意：编辑模式下 clear_on_submit 设为 False 以防误清空
    
    col1, col2 = st.columns(2)
    title = col1.text_input("作品标题", value=default_title, placeholder="例如：龙吟茶礼")
    category = col2.text_input("分类标签", value=default_category, placeholder="例如：AI PACKAGING")
    
    desc = st.text_area("作品描述", value=default_desc, height=150)
    
    st.markdown("---")
    st.markdown("**📂 资源文件管理**")
    
    # 封面图处理
    col_cov1, col_cov2 = st.columns([1, 2])
    if mode == "✏️ 编辑已有作品" and old_cover:
        col_cov1.image(old_cover, caption="当前封面", width=100)
        cov_label = "更换封面图 (留空则保留原图)"
    else:
        cov_label = "上传封面图 (必须)"
        
    cover_file = col_cov2.file_uploader(cov_label, type=['jpg', 'png', 'jpeg', 'webp'])

    # 视频处理
    video_file = st.file_uploader(
        "视频文件 (可选 MP4) - 留空则保留原视频/不上传", 
        type=['mp4']
    )
    
    # 多图处理
    detail_files = st.file_uploader(
        "更多详情插图 (可选多张) - 注意：上传新图将替换旧图列表", 
        type=['jpg', 'png', 'jpeg', 'webp'], 
        accept_multiple_files=True
    )
    
    submit_label = "🚀 发布新作品" if mode == "➕ 新建作品" else "💾 保存修改"
    submitted = st.form_submit_button(submit_label, type="primary")

    if submitted:
        # 验证必填项
        # 如果是新建：必须有图。如果是编辑：没上传图可以复用旧图。
        final_cover_path = save_uploaded_file(cover_file)
        if mode == "✏️ 编辑已有作品" and final_cover_path is None:
            final_cover_path = old_cover # 沿用旧图
            
        if not title:
            st.error("❌ 标题不能为空！")
        elif not final_cover_path:
            st.error("❌ 必须有一张封面图！")
        else:
            # 1. 处理视频
            final_video_path = save_uploaded_file(video_file)
            if final_video_path is None and mode == "✏️ 编辑已有作品":
                final_video_path = old_video # 沿用旧视频

            # 2. 处理多图
            # 如果用户上传了新图，就用新的；否则如果是编辑模式，保留旧的
            final_detail_paths = []
            if detail_files:
                for f in detail_files:
                    p = save_uploaded_file(f)
                    if p: final_detail_paths.append(p)
            elif mode == "✏️ 编辑已有作品":
                final_detail_paths = old_images

            # 3. 构建数据对象
            new_project = {
                "id": int(time.time()), 
                "title": title,
                "category": category,
                "desc": desc,
                "cover": final_cover_path,
                "video": final_video_path,
                "images": final_detail_paths
            }
            
            # 4. 保存逻辑
            if mode == "➕ 新建作品":
                current_data.insert(0, new_project) # 插到最前面
                st.success("✅ 新作品发布成功！")
            else:
                # 编辑模式：替换原有位置的数据
                current_data[edit_index] = new_project
                st.success(f"✅ 《{title}》修改已保存！")

            save_data(current_data)
            time.sleep(1)
            st.rerun()

# --- 底部：删除功能 ---
if mode == "✏️ 编辑已有作品":
    st.markdown("---")
    with st.expander("🗑 删除此作品 (危险区域)"):
        st.warning(f"你确定要删除 **{default_title}** 吗？此操作不可恢复。")
        if st.button("确认删除", type="secondary"):
            del current_data[edit_index]
            save_data(current_data)
            st.toast("已删除！")
            time.sleep(1)
            st.rerun()
