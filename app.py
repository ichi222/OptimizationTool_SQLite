import sqlite3
import streamlit as st
import pandas as pd
from optimizer import optimize_design
from utils import plot_cost_vs_safety, export_results

# データベース接続と初期化
def init_db():
    conn = sqlite3.connect("materials.db")
    c = conn.cursor()
    # 材料テーブルの作成
    c.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            cost_per_m2 REAL NOT NULL,
            strength REAL NOT NULL
        )
    """)
    conn.commit()
    return conn

conn = init_db()

# CRUD 操作用関数
def get_materials():
    c = conn.cursor()
    c.execute("SELECT * FROM materials")
    rows = c.fetchall()
    return rows

def add_material(name, cost_per_m2, strength):
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO materials (name, cost_per_m2, strength) VALUES (?, ?, ?)",
            (name, cost_per_m2, strength)
        )
        conn.commit()
        st.success(f"材料 '{name}' を追加しました！")
    except sqlite3.IntegrityError:
        st.error("この材料はすでに存在します。")

def update_material(id, cost_per_m2, strength):
    c = conn.cursor()
    c.execute(
        "UPDATE materials SET cost_per_m2 = ?, strength = ? WHERE id = ?",
        (cost_per_m2, strength, id)
    )
    conn.commit()
    st.success("材料を更新しました！")

def delete_material(id):
    c = conn.cursor()
    c.execute("DELETE FROM materials WHERE id = ?", (id,))
    conn.commit()
    st.success("材料を削除しました！")

# タイトル
st.title("土木構造物の設計最適化ツール")

# CRUD 操作用セクション
st.sidebar.header("材料管理 (CRUD)")
crud_action = st.sidebar.selectbox("操作を選択", ["材料一覧", "材料を追加", "材料を編集", "材料を削除"])

if crud_action == "材料一覧":
    st.subheader("現在の材料一覧")
    materials = get_materials()
    df = pd.DataFrame(materials, columns=["ID", "名前", "コスト (円/m²)", "強度 (kN/m²)"])
    st.dataframe(df)

elif crud_action == "材料を追加":
    st.subheader("新しい材料を追加")
    new_material = st.text_input("材料名")
    new_cost = st.number_input("コスト（円/m²）", min_value=0.0, step=100.0)
    new_strength = st.number_input("強度（kN/m²）", min_value=0.0, step=10.0)
    
    if st.button("追加"):
        add_material(new_material, new_cost, new_strength)

elif crud_action == "材料を編集":
    st.subheader("既存の材料を編集")
    materials = get_materials()
    df = pd.DataFrame(materials, columns=["ID", "名前", "コスト (円/m²)", "強度 (kN/m²)"])
    st.dataframe(df)

    material_id = st.number_input("編集する材料のID", min_value=1, step=1)
    edited_cost = st.number_input("新しいコスト（円/m²）", min_value=0.0, step=100.0)
    edited_strength = st.number_input("新しい強度（kN/m²）", min_value=0.0, step=10.0)

    if st.button("更新"):
        update_material(material_id, edited_cost, edited_strength)

elif crud_action == "材料を削除":
    st.subheader("材料を削除")
    materials = get_materials()
    df = pd.DataFrame(materials, columns=["ID", "名前", "コスト (円/m²)", "強度 (kN/m²)"])
    st.dataframe(df)

    material_id = st.number_input("削除する材料のID", min_value=1, step=1)

    if st.button("削除"):
        delete_material(material_id)

# 設計条件の入力セクション
st.sidebar.header("設計条件")
length = st.sidebar.number_input("橋梁の長さ（m）", min_value=1.0, value=50.0, step=1.0)
width = st.sidebar.number_input("橋梁の幅（m）", min_value=1.0, value=10.0, step=1.0)
max_load = st.sidebar.number_input("最大許容荷重（kN）", min_value=1.0, value=500.0, step=10.0)

# データベースから材料を取得
materials = get_materials()
material_names = [m[1] for m in materials]
material_properties = {m[1]: {"cost_per_m2": m[2], "strength": m[3]} for m in materials}

selected_materials = st.sidebar.multiselect("使用可能な材料", options=material_names, default=material_names)

# 最適化ボタン
if st.sidebar.button("最適化を実行"):
    if not selected_materials:
        st.error("少なくとも1つの材料を選択してください。")
    else:
        result = optimize_design(length, width, max_load, selected_materials, material_properties)
        if "error" in result:
            st.error(result["error"])
        else:
            st.subheader("最適化結果")
            st.write(f"最適材料: {result['material']}")
            st.write(f"最適長さ: {result['length']:.2f} m")
            st.write(f"最適幅: {result['width']:.2f} m")
            st.write(f"推定コスト: {result['cost']:.2f} 円")
            plot_cost_vs_safety(result["costs"], result["safety_margins"])

            # 結果のエクスポート
            result_df = pd.DataFrame([result])
            export_results(result_df)
