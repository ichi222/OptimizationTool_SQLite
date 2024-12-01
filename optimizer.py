from scipy.optimize import minimize

def optimize_design(length, width, max_load, materials, material_properties):
    selected_materials = [m for m in materials if m in material_properties]

    def objective(x):
        # 目的関数（コスト最小化）
        material = selected_materials[int(x[0])]
        area = x[1] * x[2]  # 長さ × 幅
        cost = material_properties[material]["cost_per_m2"] * area
        return cost

    def constraint_strength(x):
        # 安全性の制約（応力 <= 材料の強度）
        material = selected_materials[int(x[0])]
        stress = max_load / (x[1] * x[2])  # 荷重 / 面積
        return material_properties[material]["strength"] - stress

    # 初期値
    x0 = [0, length, width]

    # 制約条件
    constraints = [{"type": "ineq", "fun": constraint_strength}]

    # 設計空間の境界
    bounds = [(0, len(selected_materials) - 1), (1, length), (1, width)]

    result = minimize(objective, x0, bounds=bounds, constraints=constraints)
    if result.success:
        optimal_material = selected_materials[int(result.x[0])]
        optimal_length = result.x[1]
        optimal_width = result.x[2]
        return {
            "material": optimal_material,
            "length": optimal_length,
            "width": optimal_width,
            "cost": result.fun,
            "costs": [result.fun],  # コスト履歴（単純化）
            "safety_margins": [constraint_strength(result.x)],  # 安全性履歴
        }
    else:
        return {"error": "Optimization failed"}
