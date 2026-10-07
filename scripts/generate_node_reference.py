#!/usr/bin/env python3
"""Generate readable Omoo Nodes references from inspected node metadata."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


BEHAVIOR_NOTES = {
    "O Image Info": "读取合成图像的尺寸关系，输出可用于分辨率无关运算的相对尺寸。",
    "O Relight": "结合图像、法线与遮罩，按给定方向和颜色重新计算方向光，并同时输出光照分量。",
    "O Stroke": "综合 Matte、Depth 与 Normal 边缘生成可抖动、可调粗细的合成描边，并叠加到原图。",
    "O Align Edge Ends": "迭代拉齐距离阈值内的开放边端点，适合清理后续连接或管线生成前的边。",
    "O Blend": "在目标几何与 Source 的对应位置之间按 Factor 混合选中元素。",
    "O Capsule": "生成可独立控制顶部和底部封口的胶囊网格，并输出区域选择与 UV。",
    "O Center": "把几何包围盒中心移动到指定 Center。",
    "O Center Line": "从网格估算并平滑中心线，输出便于进一步曲线处理的边几何。",
    "O Connect Adjacent": "按 Range 为相邻点建立连接，使用 Selection 限定参与范围。",
    "O Curve Deform": "沿 Curve 弯曲或贴合几何，可控制轴向、偏移、倾斜、权重与中心策略。",
    "O Curve Distance Texture": "计算采样位置到曲线或边的距离场，并用 Radius Offset 调整等值面。",
    "O Curve Flow Texture": "从曲线切线、法线或扭转方向生成向量流场，可重采样和平滑。",
    "O Curve to Edge": "把 Blender Curve 转成仅含边的 Mesh 表示。",
    "O Debug Direction": "把几何上的方向向量可视化，并输出规范化后的方向。",
    "O Debug Direction Field": "在平面或体积采样网格上可视化向量场。",
    "O Debug Edge": "把边转换为可见线框，并把给定属性同步到调试结果。",
    "O Debug Field": "在规则采样网格上把向量或数值场转成可见颜色和调试几何。",
    "O Debug Integer": "把整数或 ID 映射为颜色等可视表示，便于检查分组。",
    "O Debug UV": "展开或直接显示 UV，并突出 UV Seam、边界及岛屿差异。",
    "O Delete Small Parts": "按连通部分大小删除低于 Threshold 的碎片。",
    "O Displace": "沿法线、指定方向或向量场移动选中几何，支持 Strength、Height 与 Midlevel。",
    "O Edge to Curve": "把仅含边的 Mesh 转成 Curve。",
    "O Exploded View": "按连通块或 Group ID 从整体中心向外缩放各部分，形成爆炸视图。",
    "O Fast Remesh": "以较少步骤重建较均匀拓扑，并可松弛、平滑着色及尝试修复 UV。",
    "O Geometry Info": "输出几何的包围盒尺寸、中心点与顶点中位位置。",
    "O Grid Distribute": "在网格表面按间距分布点，支持随机筛选、半径约束和松弛。",
    "O Helix": "按角度、半径和高度生成螺旋边。",
    "O ID Selection": "按 ID 字段选择元素，并支持反选。",
    "O Index Selection": "按 Index 字段选择元素，并支持反选。",
    "O Is Edge Boundary": "判断当前边是否位于网格边界。",
    "O Is UV Split": "判断边两侧 UV 是否断开，并区分同岛与异岛。",
    "O Mask by Distance": "计算到 Source 的距离，输出距离、遮罩以及被遮罩的几何。",
    "O Mask by Selection": "把一个 Selection 扩展成基于距离或拓扑的平滑遮罩。",
    "O Match Size": "按目标 Size 缩放几何并把中心对齐到指定 Center。",
    "O Mesh Boolean": "提供 Union、Intersect、Difference 等布尔模式，并带属性平滑、体素预览和交线输出。",
    "O Mesh Distance Texture": "输出采样位置到网格表面的有符号或无符号距离。",
    "O Mesh Flow Texture": "从网格表面方向生成向量流场，可控制强度、反向与作用半径。",
    "O Mix Color": "按 Factor 混合两种颜色。",
    "O Nearby Selection": "选择 Point Index 周围 Range 内的点，可排除自身或反选。",
    "O Noise Texture": "生成可重映射范围和中点的噪声数值与向量，供位移或场运算使用。",
    "O Normalize Attribute ": "在选中域上把浮点 Attribute 归一化，输出标准化结果。",
    "O Object to Tangent Space": "结合 UV Tangent 与 Normal，把对象空间方向转换到切线空间。",
    "O Pick Instance": "按当前求值元素的 Index 从输入实例集合中挑选单个实例。",
    "O Point Deform": "根据 Source 点相对 Rest Position 的变化，把捕获到的变形传递给目标几何。",
    "O Point Grid": "在选定平面或体积范围内生成规则点阵，可限制内外区域。",
    "O Points Distance Texture": "输出采样位置到点集的距离场，并支持半径偏移。",
    "O Points Flow Texture": "根据点集生成向量流场，可控制方向、强度和作用半径。",
    "O Position Selection": "按坐标轴、比较方式与 A/B 阈值选择位置范围。",
    "O Project": "按最近距离或正负方向射线把选中几何投射到 Source，并支持自定义方向和权重。",
    "O Quad Sphere": "生成以四边面为主的球体并输出 UV。",
    "O Random Direction": "在给定 Direction 周围生成随机方向与旋转，支持径向和轴向扩散。",
    "O Random Instance Index": "按 A–E 权重随机生成 Instance Index。",
    "O Random Selection": "按 Factor、ID 与 Seed 生成稳定的随机选择。",
    "O Region Selection": "判断元素是否位于 Region Mesh 内，并支持反选。",
    "O Relax": "迭代平滑点分布，可固定边界、投射回 Source 并按网格岛限制。",
    "O Resample Edge": "把边转换为曲线后按 Length 重采样，再转回边并合并近点。",
    "O Rest Position": "保存并输出几何的 Rest Position，供后续变形与张力计算使用。",
    "O Scene Time": "把场景时间按 Step 量化，输出步进秒数。",
    "O Screw": "围绕指定中心轴旋转并推进输入网格，生成旋转体或螺纹结构。",
    "O Selection": "读取指定名称的布尔选择属性，并支持反选。",
    "O Set Edge Radius": "在选中边上存储或设置后续管线节点使用的半径。",
    "O Shortest Paths": "从 Root 计算加权最短路径，输出路径边、总成本与路径因子。",
    "O Smooth": "迭代平滑选中几何，可通过 Pin Sharp 和 Pin Boundary 保留特征。",
    "O Smooth Attributes": "在指定域上迭代平滑 Float、Vector 或 Color 属性。",
    "O Solidfy": "为网格增加厚度，并输出侧面选择。",
    "O Store Selection": "把当前 Selection 以给定 Name 存入指定几何域。",
    "O Symmetry": "按轴镜像或径向复制几何，生成对称结构。",
    "O Tension": "比较当前位置与 Rest Position，输出形变张力场。",
    "O Timing": "在指定第 N 帧条件下输出布尔时序信号。",
    "O Torus": "生成可控主半径、次半径和分段数的圆环网格及 UV。",
    "O Transfer Attributes": "从 Source 采样并写入 Float、Integer、Vector 或 Color 属性，支持跨域和分组。",
    "O Transfer Material": "按采样位置或 UV Island 从 Source 转移材质分配。",
    "O Transfer UV": "从 Source 向目标网格转移 UV，并可按 UV Island 和 Fix 范围修正断裂。",
    "O Transform": "对选中几何或组件应用平移、旋转、缩放或矩阵，并支持软选择。",
    "O Tube": "把边转换为可调分辨率、半径和厚度的管状网格，可封口和连接近端点。",
    "O UV Island": "根据 UV Split 生成稳定的 UV Island 标识。",
    "O UV Tangent": "从网格 UV 计算并存储 UV Tangent。",
    "O Voxel Remesh": "体素化并重建网格，可控制分辨率、适应性、拓扑旋转与后续松弛。",
    "O Wireframe": "把选中网格边转换成具有 Radius 和 Resolution 的线框几何。",
    "O Background": "构建可分别控制可见背景、环境光和 Cycles 透射行为的 World Shader。",
    "O Circle": "生成二维圆形遮罩 Fac 与径向 Gradient。",
    "O Ensure UV": "规范输入纹理坐标，确保下游二维纹理获得稳定 UV。",
    "O Grid": "把坐标量化或重复为 X×Y 网格坐标。",
    "O Linear": "按 Angle 生成线性 Fac 与 Gradient。",
    "O Pixelate": "按 X×Y 分辨率量化二维坐标，形成像素化采样。",
    "O Square": "生成可调 X/Y 尺寸的矩形遮罩 Fac 与边缘 Gradient。",
    "O Draw Shape": "把 Grease Pencil 笔画转成实体网格，可膨胀、对称、重网格和平滑。",
    "O Draw Tubes": "把 Grease Pencil 笔画转成管状网格，可对齐端点、连接、对称及重网格。",
    "O Gradient Background": "用两种颜色和线性角度生成渐变 World Shader，并保留独立环境光控制。",
    "O One Texture": "从一个 Color 或纹理信号派生粗糙度、凹凸、透明、次表面等通道，生成 Principled BSDF。",
    "O Outline": "通过几何外扩和材质设置生成倒壳式轮廓，可加入次级轮廓和松散抖动。",
    "O Random Jitter": "用随时间步进的噪声位移几何，生成稳定可控的随机抖动动画。",
}


HOUDINI_REFERENCES = {
    "O Exploded View": "https://www.sidefx.com/docs/houdini/nodes/sop/explodedview.html",
    "O Match Size": "https://www.sidefx.com/docs/houdini/nodes/sop/matchsize.html",
    "O Point Deform": "https://www.sidefx.com/docs/houdini/nodes/sop/pointdeform.html",
    "O Relax": "https://www.sidefx.com/docs/houdini/nodes/sop/relax.html",
    "O Transfer Attributes": "https://www.sidefx.com/docs/houdini/nodes/sop/attribtransfer.html",
    "O Voxel Remesh": "https://www.sidefx.com/docs/houdini/nodes/sop/remesh.html",
}


SOURCE_TITLES = {
    "O_Essentials_CompositingNodes.blend": "合成节点",
    "O_Essentials_GeometryNodes.blend": "几何节点",
    "O_Essentials_ShaderNodes.blend": "着色器节点",
    "O_Extra.blend": "O Extra",
}


USE_CASES = {
    "O Curve Deform": [
        "让文字、线缆、鳞片或重复结构沿一条曲线弯曲。",
        "先制作直线形态，再用曲线统一控制最终走势，方便反复改形。",
    ],
    "O Debug UV": [
        "在不切换 UV 编辑器的情况下检查断缝、UV 岛和拉伸问题。",
    ],
    "O Displace": [
        "把 `O Noise Texture` 接到 `Height`，制作水面起伏、地形细节或呼吸式形变。",
        "用顶点属性或绘制遮罩限制局部位移，避免整个模型一起变形。",
    ],
    "O Exploded View": [
        "制作产品拆解图、装配动画，或快速检查互相遮挡的零件。",
    ],
    "O Grid Distribute": [
        "在曲面上生成规则但不过分机械的散布点，用于植被、铆钉或面板细节。",
    ],
    "O Mesh Boolean": [
        "制作可随输入模型更新的门窗开洞、拼接结构和交叠线。",
    ],
    "O Noise Texture": [
        "驱动位移、颜色、粗糙度或随机选择，让变化保持可重复且易于调节。",
    ],
    "O One Texture": [
        "只有一张颜色贴图时，快速得到可用的材质起点，再逐项微调表面特征。",
    ],
    "O Outline": [
        "制作漫画轮廓、产品描边，或叠加轻微抖动获得手绘感。",
    ],
    "O Point Deform": [
        "用低模代理体驱动高模、毛发或附着细节，降低复杂形变的编辑成本。",
    ],
    "O Project": [
        "把道路、贴花、线条或散布点贴到起伏表面。",
    ],
    "O Random Jitter": [
        "制作定格动画、手绘抖线或机械部件的轻微振动。",
    ],
    "O Relight": [
        "在合成阶段补一盏可控方向光，快速调整角色或产品的受光方向。",
    ],
    "O Transfer Attributes": [
        "重拓扑或重网格后，把颜色、遮罩、方向等数据从原模型传回新模型。",
    ],
    "O Voxel Remesh": [
        "把扫描、布尔碎片或相交网格先统一成连续表面，再继续平滑和变形。",
    ],
}


INPUT_PURPOSES = {
    "A": "提供第一组参与比较、混合或计算的数据。",
    "Adaptivity": "减少平坦区域的面数，同时尽量保留轮廓和细节。",
    "Align Ends": "决定是否整理并对齐开放端点。",
    "Align Iterations": "控制端点对齐要重复计算多少次；次数越多，整理越充分。",
    "Align Threshold": "决定相距多近的端点才会被视为需要对齐。",
    "Alpha": "控制整体透明度。",
    "Angle": "控制旋转角度或方向角。",
    "Attribute": "提供要读取、处理或写回的属性值。",
    "Axial Spread": "控制随机方向沿主轴扩散的程度。",
    "Axis": "选择计算、变换或生成结构所沿的轴。",
    "B": "提供第二组参与比较、混合或计算的数据。",
    "Bump Distance": "控制由纹理明暗产生的表面凹凸幅度。",
    "Blur": "柔化结果，减弱过硬的边界或细节。",
    "Bottom Cap": "决定底部是否封口。",
    "C": "提供当前模式下的第三组数据或权重。",
    "Center": "指定操作围绕的中心位置或目标中心。",
    "Color": "提供要使用、混合或处理的颜色。",
    "Connect": "决定是否连接彼此接近或相邻的部分。",
    "Connect Distance": "决定相距多近的部分可以连接。",
    "Container": "提供用于限定内部、外部或计算范围的容器几何。",
    "Cost": "为路径计算提供每一步的代价或权重。",
    "Curve": "提供控制形状、走势或采样位置的曲线。",
    "Curve (Edge)": "提供以网格边表示的曲线。",
    "Custom": "启用或提供自定义控制方式。",
    "D": "提供当前模式下的第四组数据或权重。",
    "Depth": "提供深度信息或控制沿深度方向的距离。",
    "Detail": "控制噪声中小尺度细节的丰富程度。",
    "Direction": "指定效果、投射或形变前进的方向。",
    "Distance Threshold": "决定距离达到什么条件时才产生效果。",
    "Distortion": "控制形状或纹理被扰动的程度。",
    "E": "提供当前模式下的第五组数据或权重。",
    "Emission Strength": "控制材质自身发光的亮度。",
    "Edge": "提供要处理、筛选或转换的边。",
    "Evaluate on": "选择在哪一类几何元素上计算结果。",
    "Exclude Self": "排除元素自身，避免把自己算作邻近目标。",
    "Exposure": "整体提亮或压暗结果。",
    "Factor": "控制两种状态之间的混合比例或效果强度。",
    "Field": "提供需要采样或可视化的场数据。",
    "Fill Caps": "决定开放截面是否封口。",
    "Fit to Curve": "让变形长度适配控制曲线，避免只使用曲线的一部分或超出曲线。",
    "Fix": "选择需要固定、不参与调整的部分。",
    "Fix Topo Steps": "控制拓扑修复过程尝试多少步。",
    "Fix UV": "在拓扑变化后尝试修复和保留原有 UV。",
    "Flat": "决定是否使用平直、无平滑过渡的结果。",
    "Float": "提供要处理或传递的小数属性。",
    "Frequency": "控制变化出现得有多密集。",
    "Gamma": "调整明暗中间调。",
    "Geometry": "提供要处理的几何。",
    "Grease Pencil": "提供要转换成实体形状或管线的 Grease Pencil 笔画。",
    "Group ID": "用编号把元素分组，让每组独立计算。",
    "Height": "提供位移高度或形状起伏。",
    "Hue": "调整颜色的色相。",
    "ID": "提供稳定编号，用于选择、分组或可重复随机。",
    "Image": "提供要分析或处理的图像。",
    "Index": "按元素序号控制选择或计算。",
    "Inflate": "让形状沿表面法线向外或向内鼓起。",
    "Inside": "决定使用区域内部还是外部。",
    "Integer": "提供要处理或传递的整数属性。",
    "Invert": "反转当前选择、遮罩或判断结果。",
    "IOR": "控制材质折射率，并影响反射与透射的观感。",
    "Iterations": "控制重复计算次数；次数越多通常越充分，也会更慢。",
    "Lacunarity": "控制噪声不同尺度之间的频率增长速度。",
    "Length": "控制生成、重采样或搜索使用的长度。",
    "Light": "提供光照颜色或光照信息。",
    "Location": "指定位置或平移量。",
    "Loose": "决定是否处理没有连接成面的松散点和边。",
    "Major Radius": "控制圆环或螺旋主体的半径。",
    "Major Segments": "控制主体一圈的分段精细度。",
    "Mask": "限制效果的作用范围；黑白或数值可形成渐变过渡。",
    "Matte": "提供前景遮罩或抠像结果。",
    "Max": "设置映射、筛选或限制使用的上限。",
    "Max Distance": "限制搜索、投射或影响能够到达的最远距离。",
    "Merged": "决定是否把生成结果中彼此重合或接近的部分合并。",
    "Menu": "选择节点的工作模式；切换后相关输入也会随之变化。",
    "Merge Distance": "决定相距多近的点会被合并。",
    "Mesh": "提供要处理或作为参考的网格。",
    "Mesh Island": "按互不连接的网格块分别处理。",
    "Messy": "加入不规则变化，避免端点或排列显得过于整齐。",
    "Metallic": "控制表面从非金属到金属的程度。",
    "Method": "选择节点采用的计算方法。",
    "Midlevel": "指定高度信号中代表「不发生位移」的基准值。",
    "Min": "设置映射、筛选或限制使用的下限。",
    "Minor Radius": "控制圆环截面或次级结构的半径。",
    "Minor Segments": "控制截面一圈的分段精细度。",
    "Mode": "选择节点采用的工作方式。",
    "N": "指定触发或采样使用的第几个时间步。",
    "Name": "指定要读取或写入的属性名称。",
    "Normal": "提供表面朝向，用于光照、投射或方向计算。",
    "Normal Smooth": "柔化用于计算的法线，减少方向场中的突变。",
    "Normal Threshold": "决定法线方向差异多大时才视为不同区域。",
    "Normal/Twist/Tangent": "选择使用法线、扭转或切线来构建方向。",
    "Normalize": "把结果整理到统一尺度，便于后续混合或比较。",
    "Offset": "在原位置、时间或数值基础上增加偏移。",
    "Pin Boundary": "固定边界，避免平滑或松弛时轮廓收缩。",
    "Pin Sharp": "尽量固定尖锐特征，避免被平滑掉。",
    "Point Index": "指定作为中心或参考的点序号。",
    "Points": "提供用于采样、变形或生成场的点。",
    "Position": "提供要计算或采样的空间位置。",
    "Preview": "启用便于观察过程的预览结果。",
    "Primary Axis": "选择形变或对齐使用的主轴。",
    "Radial": "控制是否围绕中心按径向方式计算。",
    "Radius": "控制影响范围、管线粗细或圆形尺寸。",
    "Radius Offset": "在现有半径基础上增加或减少距离。",
    "Radius Scale": "按比例放大或缩小已有半径。",
    "Random": "加入随机变化，打破过于规则的结果。",
    "Random Selection": "限制哪些随机选中的元素参与处理。",
    "Range": "控制搜索、选择或影响覆盖的范围。",
    "Ray": "选择沿射线方向进行投射或查找。",
    "Region Mesh": "提供用于判断内外区域的网格。",
    "Relax Iterations": "控制松弛计算重复次数；次数越多，分布越均匀。",
    "Relax Weight": "控制松弛对当前位置的影响强度。",
    "Remesh": "决定是否重建网格拓扑。",
    "Resample Length": "控制重采样后相邻点或边的大致间距。",
    "Resolution": "控制生成结果或采样网格的精细度。",
    "Rest Position": "提供未变形时的位置，作为形变比较基准。",
    "Rest Positon": "提供未变形时的位置，作为形变比较基准。",
    "Reverse": "反转方向、顺序或判断结果。",
    "Rings": "控制环形结构沿长度方向的分段数量。",
    "Root": "指定最短路径开始计算的根元素。",
    "Rotation": "指定旋转量或朝向。",
    "Roughness": "控制表面高光从清晰到粗糙的程度。",
    "Roughness Max": "设置由输入纹理推导粗糙度时的最高值。",
    "Roughness Min": "设置由输入纹理推导粗糙度时的最低值。",
    "Sample Group ID": "限定从相同分组中采样，避免数据串到其他组。",
    "Sample Position": "指定去参考几何上查询数据的位置。",
    "Saturation": "调整颜色饱和度。",
    "Scale": "整体放大或缩小形状、坐标或效果尺度。",
    "Screw": "控制绕轴旋转同时前进的螺旋量。",
    "Seam": "提供接缝选择，用于切分或检查 UV。",
    "Secondary Axis": "选择辅助轴，帮助确定完整朝向。",
    "Secondary (Eevee)": "在 Eevee 中启用次级轮廓层。",
    "Seed": "更换随机结果，同时保持同一数值下结果稳定。",
    "Segments": "控制生成结构沿主要方向的分段精细度。",
    "Selection": "限制效果作用范围；未选中的部分保持不变。",
    "Shade Smooth": "决定结果是否使用平滑着色。",
    "Side Segments": "控制侧面沿长度方向的分段精细度。",
    "Size": "控制整体尺寸或目标包围盒大小。",
    "Smooth": "柔化形状、属性或过渡。",
    "Smooth Intersecting": "柔化布尔运算产生的相交边，减弱生硬折线。",
    "Smooth Iterations": "控制平滑重复次数；次数越多，结果越柔和。",
    "Smooth Weight": "控制每次平滑对原结果的影响强度。",
    "Soft": "让硬选择变成带渐变的柔和影响。",
    "Soft Iterations": "控制柔和范围向外扩展和过渡的次数。",
    "Solid": "决定结果是否保持或生成封闭实体。",
    "Source": "提供用于采样、匹配、投射或比较的参考几何。",
    "Source Mesh Island": "按参考网格的独立块分组采样，避免跨块传递。",
    "Space": "选择坐标或变换所处的空间。",
    "Spacing": "控制相邻点或实例之间的目标间距。",
    "Spread": "控制随机方向或分布向外扩散的程度。",
    "Step": "控制时间或计算按多大步长前进。",
    "Step Size": "控制每次迭代移动或采样的距离。",
    "Steps": "控制过程被拆分成多少步。",
    "Strength": "控制效果的整体强弱。",
    "Subsurface Scale": "控制次表面散射深入材质内部的距离。",
    "Symmetry": "选择要生成或保留的对称方向。",
    "Thickness": "控制实体、描边或管壁的厚度。",
    "Threshold": "设置判断或筛选生效的分界值。",
    "Tilt": "控制曲线截面沿路径的扭转。",
    "Top Cap": "决定顶部是否封口。",
    "Topo Rotation": "沿网格拓扑调整方向，使重建后的边流转向。",
    "Transform": "提供完整的平移、旋转和缩放变换。",
    "Translation": "指定平移量。",
    "Transmission (Cycles)": "控制 Cycles 中光线穿过材质的程度。",
    "Type": "选择节点要处理的数据或生成结果类型。",
    "Unsigned": "只保留距离大小，不区分表面内外。",
    "UV": "提供纹理坐标，用于采样、转移或空间计算。",
    "UV Island": "按 UV 岛分组或限制处理范围。",
    "UV Seam": "提供 UV 接缝选择。",
    "UV Tangent": "提供沿 UV 方向计算得到的表面切线。",
    "Value": "提供要处理、映射或混合的数值。",
    "Vector": "提供要处理、转换或可视化的向量。",
    "W": "控制四维噪声的额外维度，常用于制作连续动画。",
    "Weight": "控制每个元素受效果影响的程度。",
    "X": "控制 X 方向的尺寸、分段或数值。",
    "Y": "控制 Y 方向的尺寸、分段或数值。",
    "Alpha Max": "设置由输入纹理推导透明度时的最高值。",
    "Alpha Min": "设置由输入纹理推导透明度时的最低值。",
    "on": "打开或关闭这一项处理。",
}


OUTPUT_PURPOSES = {
    "Attribute": "输出处理或采样后的属性。",
    "Boolean": "输出布尔判断结果。",
    "Bottom": "输出底部区域选择。",
    "BSDF": "输出可直接连接到材质表面的着色结果。",
    "Center Point": "输出包围盒中心位置。",
    "Color": "输出计算后的颜色。",
    "Curve": "输出处理后的曲线。",
    "Debug": "输出便于在视口中检查结果的调试几何。",
    "Different Island": "标记边两侧属于不同 UV 岛的位置。",
    "Direction": "输出计算后的方向。",
    "Distance": "输出到参考目标的距离。",
    "Edge": "输出处理或筛选后的边。",
    "Fac": "输出可作为遮罩或混合系数使用的数值。",
    "Factor": "输出可用于后续混合或控制强度的系数。",
    "Geometry": "输出处理后的几何。",
    "Gradient": "输出形状边缘或方向上的渐变值。",
    "Image": "输出处理后的图像。",
    "Instance": "输出选中的实例。",
    "Instance Index": "输出要从实例集合中选择的序号。",
    "Intersecting Edges": "标记布尔运算产生的相交边。",
    "Is Edge Boundary": "标记处于网格边界的边。",
    "Is UV Split": "标记 UV 在边两侧断开的位置。",
    "Light": "输出单独的光照分量。",
    "Mask": "输出可继续用于限制其他效果的遮罩。",
    "Median Point": "输出顶点位置的中位点。",
    "Mesh": "输出处理后的网格。",
    "Normal": "输出计算或处理后的表面法线。",
    "O Tension": "输出形变产生的张力值。",
    "Points": "输出生成或处理后的点。",
    "Relative Size": "输出相对于参考分辨率的尺寸比例。",
    "Rest Positon": "输出记录下来的未变形位置。",
    "Result": "输出节点最终计算结果。",
    "Rotation": "输出计算后的旋转。",
    "Same Island": "标记边两侧属于同一 UV 岛的位置。",
    "Selection": "输出满足条件的元素选择。",
    "Shader": "输出可连接到材质或世界表面的着色器。",
    "Side": "输出侧面区域选择。",
    "Size": "输出几何包围盒尺寸。",
    "Step Seconds": "输出按步长量化后的时间。",
    "Stroke": "输出单独的描边图像。",
    "Top": "输出顶部区域选择。",
    "Total Cost": "输出从根元素到当前位置的累计路径代价。",
    "UV Island": "输出稳定的 UV 岛编号。",
    "UV Map": "输出生成或转移后的 UV 坐标。",
    "UV Tangent": "输出沿 UV 方向的表面切线。",
    "Value": "输出计算后的数值。",
    "Vector": "输出计算后的向量。",
}


NODE_PARAMETER_PURPOSES = {
    ("O Displace", "INPUT", "Direction"): "指定顶点移动方向；使用法线模式时通常无需单独连接。",
    ("O Displace", "INPUT", "Height"): "用明暗或数值决定每个位置移动多少，可接纹理、属性或动画信号。",
    ("O Displace", "INPUT", "Midlevel"): "指定高度信号中的静止点；等于此值的位置不移动。",
    ("O Displace", "INPUT", "Strength"): "统一放大、缩小或反转位移幅度。",
    ("O Displace", "INPUT", "Vector"): "直接提供每个位置的三维移动量，适合由方向场同时控制方向和距离。",
    ("O Noise Texture", "INPUT", "Detail"): "增加更小尺度的噪声层次；提高后会更丰富，也更碎。",
    ("O Noise Texture", "INPUT", "Roughness"): "控制不同尺度噪声混合后的粗糙程度。",
    ("O Noise Texture", "INPUT", "Sample Position"): "指定噪声在空间中的采样位置；移动它可以让纹理流动。",
    ("O Noise Texture", "INPUT", "Scale"): "控制噪声纹理的空间尺寸；数值越大，纹理变化越密。",
    ("O Noise Texture", "INPUT", "Vector"): "提供噪声采样坐标；移动坐标即可让噪声在空间中流动。",
    ("O Noise Texture", "INPUT", "W"): "推动噪声随时间连续变化，适合制作不会跳帧的动态起伏。",
    ("O Noise Texture", "OUTPUT", "Value"): "输出经过范围与中点整理的噪声数值，可直接驱动位移或遮罩。",
    ("O Noise Texture", "OUTPUT", "Vector"): "输出三方向噪声，可直接用作方向或位置扰动。",
    ("O Random Jitter", "INPUT", "Frequency"): "控制抖动噪声的空间密度；越高时，相邻位置的变化越细碎。",
    ("O Random Jitter", "INPUT", "Step Size"): "控制随机形态间隔多少帧更新一次；越大时，每个形态停留越久。",
    ("O Random Jitter", "INPUT", "Strength"): "控制每次抖动的位移幅度。",
}


def parameter_purpose(asset_name: str, socket: dict[str, Any]) -> str:
    """Return a concise, human-readable explanation for one socket."""
    name = socket["name"].rstrip()
    key = (asset_name, socket["in_out"], name)
    if key in NODE_PARAMETER_PURPOSES:
        return NODE_PARAMETER_PURPOSES[key]
    purposes = INPUT_PURPOSES if socket["in_out"] == "INPUT" else OUTPUT_PURPOSES
    if name in purposes:
        return purposes[name]

    lowered = name.lower()
    if lowered.endswith(" iterations"):
        return "控制这一处理重复计算的次数；次数越多，结果通常越充分。"
    if lowered.endswith(" weight"):
        return f"控制「{name.removesuffix(' Weight')}」对最终结果的影响强度。"
    if lowered.endswith(" range"):
        return f"限制「{name.removesuffix(' Range')}」相关处理的作用范围。"
    if socket["in_out"] == "INPUT":
        return f"控制节点中的「{name}」设置。"
    return f"输出节点计算得到的「{name}」。"


def socket_label(socket: dict[str, Any]) -> str:
    """Include the panel path when identical names belong to different modes."""
    name = socket["name"].rstrip()
    panel = [part.rstrip() for part in socket.get("panel", []) if part.rstrip()]
    if not panel:
        return name
    if panel[-1] == name:
        return " / ".join(panel)
    return " / ".join([*panel, name])


def asset_section(asset: dict[str, Any]) -> str:
    """Render one asset as a short user manual."""
    name = asset["name"]
    display_name = name.rstrip()
    behavior = BEHAVIOR_NOTES.get(name, "根据节点接口和内部节点图提供对应功能。")
    reference = HOUDINI_REFERENCES.get(name)
    if reference:
        behavior += f" 概念命名可参照 [Houdini 同名或近似节点]({reference})。"

    lines = [
        f"### {display_name}",
        "",
        behavior,
        "",
    ]
    use_cases = USE_CASES.get(name, [])
    if use_cases:
        lines.extend(["#### 妙用", ""])
        lines.extend(f"- {use_case}" for use_case in use_cases)
        lines.append("")

    sockets_by_direction = {
        "INPUT": [
            socket for socket in asset["interface"] if socket["in_out"] == "INPUT"
        ],
        "OUTPUT": [
            socket for socket in asset["interface"] if socket["in_out"] == "OUTPUT"
        ],
    }
    for direction, title in (("INPUT", "输入"), ("OUTPUT", "输出")):
        sockets = sockets_by_direction[direction]
        if not sockets:
            continue
        lines.extend([f"#### {title}", ""])
        for socket in sockets:
            label = socket_label(socket)
            purpose = parameter_purpose(name, socket)
            lines.append(f"- `{label}`：{purpose}")
        lines.append("")

    lines.append("")
    return "\n".join(lines)


def render_reference(
    title: str,
    assets: list[dict[str, Any]],
) -> str:
    """Render one library reference document."""
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for asset in assets:
        by_source[asset["source_file"]].append(asset)

    lines = [
        f"# {title} 节点参考",
        "",
        f"本页收录 {len(assets)} 个资产节点，重点说明节点能做什么、参数如何影响结果，以及值得尝试的用法。",
        "",
        "机器接口信息由 `node-catalog.json` 单独维护。"
        "同名输入属于不同模式时，会用「面板 / 参数」标明它所在的位置。",
        "",
        "## 快速索引",
        "",
    ]
    for source, source_assets in by_source.items():
        lines.append(
            f"- {SOURCE_TITLES.get(source, source)}："
            + "、".join(f"`{asset['name'].rstrip()}`" for asset in source_assets)
        )
    lines.append("")

    for source, source_assets in by_source.items():
        lines.extend(
            [
                f"## {SOURCE_TITLES.get(source, source)}",
                "",
            ]
        )
        for asset in source_assets:
            lines.append(asset_section(asset))
    return "\n".join(lines).rstrip() + "\n"


def apply_behavior_notes(payload: dict[str, Any]) -> None:
    """Embed the shared usage notes into the machine-readable catalog."""
    missing_notes = sorted(
        asset["name"]
        for asset in payload["assets"]
        if asset["name"] not in BEHAVIOR_NOTES
    )
    if missing_notes:
        raise RuntimeError(
            "Missing behavior notes: " + ", ".join(missing_notes)
        )
    for asset in payload["assets"]:
        asset["description"] = BEHAVIOR_NOTES[asset["name"]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("library_root", type=Path)
    parser.add_argument("output_directory", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    payload = json.loads(args.catalog.read_text(encoding="utf-8"))
    apply_behavior_notes(payload)
    args.catalog.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    essentials = [
        asset
        for asset in payload["assets"]
        if asset["source_file"].startswith("O_Essentials_")
    ]
    extra = [
        asset
        for asset in payload["assets"]
        if asset["source_file"] == "O_Extra.blend"
    ]

    args.output_directory.mkdir(parents=True, exist_ok=True)
    documents = {
        "o-essentials.md": render_reference(
            "O Essentials",
            essentials,
        ),
        "o-extra.md": render_reference(
            "O Extra",
            extra,
        ),
    }
    for filename, content in documents.items():
        (args.output_directory / filename).write_text(
            content,
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
