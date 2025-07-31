
import pandas as pd
import pickle
from shapely.geometry import Point, LineString
from shapely.geometry import Polygon,MultiPoint  #多边形
import torch
from torch import nn


def load_data(file):
    data_load_file = []
    file_1 = open(file, "rb")
    data_load_file = pickle.load(file_1)
    return data_load_file

# 读取纽约市POI(兴趣点)数据CSV文件，转换为列表形式    
#poi = pd.read_csv("../data/poi_nyc.csv",sep=",").values.tolist()
#region_back = load_data("../data/region_back_merge.pickle")

# print(poi.columns.values.tolist())
# pritnln()
# 初始化区域与POI的映射字典
#region_poi={}
# 存储所有不重复的POI类别
#poi_list=[]

# 为每个区域初始化空的POI列表
#for key,value in region_back.items():
#    region_poi[key] = []

# 读取POI数据CSV文件
# 第一列：the_geom（格式如POINT (-74.097961931446 40.634604200807)）
# 第二列：FACILITY TYPE（1~13的数字类别）
poi_df = pd.read_csv("../data/poi_nyc.csv", sep=",")

# 加载区域地理数据（多边形集合）
region_back = load_data("../data/region_back_merge.pickle")

# 初始化数据结构
region_poi = {key: [] for key in region_back.keys()}  # 区域ID到POI类别的映射
poi_categories = set()  # 存储所有不重复的POI类别（1~13）

# 遍历每个POI，确定其所属的区域并记录类别
#for item in poi:
    # print(item[23], item[84], item[92])
    # 创建POI的空间点对象（基于经纬度坐标）
    #tmp_point = Point(item[3],item[0])

    #for key,value in region_back.items():
        # 判断点是否在当前区域多边形内
        #if tmp_point.intersects(value):
            #if item[23]!=" ":
                #if item[23] not in region_poi[key]:
                    #region_poi[key].append(item[23])
                #if item[23] not in poi_list:
                    #poi_list.append(item[23])
            #elif item[84]!=" ":
                #if item[84] not in region_poi[key]:
                    #region_poi[key].append(item[84])
                #if item[84] not in poi_list:
                    #poi_list.append(item[84])
#print(region_poi)
#print(poi_list)
# poi_list = ['drinking_water', 'toilets', 'school', 'hospital', 'arts_centre', 'fire_station', 'police', 'bicycle_parking', 'fountain', 'ferry_terminal', 'bench', 'cinema', 'cafe', 'pub', 'waste_basket', 'parking_entrance', 'parking', 'fast_food', 'bank', 'restaurant', 'ice_cream', 'pharmacy', 'taxi', 'post_box', 'atm', 'nightclub', 'social_facility', 'bar', 'biergarten', 'clock', 'bicycle_rental', 'community_centre', 'watering_place', 'ranger_station', 'boat_rental', 'recycling', 'payment_terminal', 'bicycle_repair_station', 'place_of_worship', 'shelter', 'telephone', 'clinic', 'dentist', 'vending_machine', 'theatre', 'charging_station', 'public_bookcase', 'post_office', 'fuel', 'doctors']

# 解析POI坐标和类别并关联到区域
for _, row in poi_df.iterrows():
    # 1. 解析坐标（从the_geom列提取经纬度）
    geom_str = row[0]  # 第一列是the_geom
    # 使用正则表达式提取括号中的坐标数值
    # 匹配格式：POINT (经度 纬度)
    coord_match = re.match(r'POINT \((-?\d+\.\d+) (-?\d+\.\d+)\)', geom_str)
    if coord_match:
        lon = float(coord_match.group(1))  # 经度
        lat = float(coord_match.group(2))  # 纬度
        poi_point = Point(lon, lat)  # 创建点对象
    else:
        continue  # 跳过格式不正确的记录

    # 2. 获取POI类别（第二列是FACILITY TYPE）
    facility_type = row[1]  # 第二列是类别数字（1~13）
    # 确保类别是整数（防止可能的格式问题）
    try:
        facility_type = int(facility_type)
    except ValueError:
        continue  # 跳过无效类别

    # 3. 确定POI所属区域并记录
    for region_id, polygon in region_back.items():
        # 检查点是否在当前区域多边形内
        if poi_point.intersects(polygon):
            # 避免重复添加同一类别到区域
            if facility_type not in region_poi[region_id]:
                region_poi[region_id].append(facility_type)
            # 记录所有出现的POI类别
            poi_categories.add(facility_type)
            break  # 找到所属区域后跳出循环


# 创建POI类别到索引的映射字典（将文本类别转换为数字标识）
#poi_dict = {}
#for idx,item in enumerate(poi_list):
    #poi_dict[item]=idx
#print("sum of the category of POI:", len(poi_dict))

# 转换区域包含的POI类别为数字索引形式
#reg_incld_poi={}
#for key,value in region_poi.items():
    #reg_incld_poi[key] = []
    #for uu in value:
        #if uu in poi_dict.keys():
            #reg_incld_poi[key].append(poi_dict[uu])
#print("reg_incld_poi:",reg_incld_poi)

# 定义POI类别到数字索引的映射字典（key为类别名称，value为0~12的数字）
# 对应关系：Residential→0, Educational Facility→1, ..., Miscellaneous→12

poi_dict = {
    "Residential": 0,
    "Educational Facility": 1,
    "Cultural Facility": 2,
    "Recreational Facility": 3,
    "Social Services": 4,
    "Transportation Facility": 5,
    "Commercial": 6,
    "Government Facility": 7,
    "Religious Institution": 8,
    "Health Services": 9,
    "Public Safety": 10,
    "Water": 11,
    "Miscellaneous": 12
}

# 打印POI类别映射信息
print("POI类别到索引的映射:", poi_dict)
print("POI类别总数:", len(poi_dict))


# 转换区域包含的POI类别为0~12的索引形式
reg_incld_poi = {}
for region_id, categories in region_poi.items():
    # 处理原始1~13的数字类别：将1→0, 2→1, ..., 13→12
    # 方式1：如果categories中是原始数字（1~13），直接减1转换
    adjusted_categories = [cat - 1 for cat in categories if 1 <= cat <= 13]
    reg_incld_poi[region_id] = adjusted_categories

print("区域包含的POI索引:", reg_incld_poi)

import pickle
# 保存处理结果
with open(r"../data/reg_incld_poi_new.pickle", "wb") as file:
    pickle.dump(reg_incld_poi, file)

with open(r"../data/poi_dict_new.pickle", "wb") as file:
    pickle.dump(poi_dict, file)

print("POI数据处理完成并保存")










