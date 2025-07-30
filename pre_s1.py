
import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString
from shapely.geometry import Polygon,MultiPoint  #多边形
import matplotlib.pyplot as plt
import json
from urllib.request import urlopen, quote
import requests
import geopy
from geopy.geocoders import Nominatim
import copy
import pickle
import time
# taxi = pd.read_csv("../data/2016_Green_Taxi_Trip_Data.csv", sep = ',')
# print(taxi[:2])

# 读取曼哈顿地区的房产销售数据Excel文件，跳过前4行无关信息
census_block = pd.read_excel("../data/rollingsales_manhattan.xlsx",skiprows = 4)
# print(census_block[:2])
print(census_block.columns.values.tolist())
# 深拷贝数据并转换为列表形式，便于逐行处理
blocks = copy.deepcopy(census_block).values.tolist()

# 提取"销售时建筑类别"列数据，作为区域分类依据
# region = census_block["BUILDING CLASS CATEGORY"].values.tolist()
region = census_block["BUILDING CLASS AT TIME OF SALE"].values.tolist()

# 获取所有不重复的建筑类别，作为区域分类的唯一标识
region_ = list(set(region))
reg_nyc_dict = {} ##113 region in manhattan
for idx,sub in enumerate(region_):
    reg_nyc_dict[sub] = idx
# print(reg_nyc_dict)
# print(len(reg_nyc_dict))
# println()

skip_num = 0 # 记录跳过的无效数据行数
region_f = {} # 存储每个建筑类别对应的地理位置列表
add_pos = {} # 存储地址到经纬度的映射（避免重复地理编码）
i= 0
NYC_house_middle = [] # 存储处理后的房产核心信息
# 遍历每一行数据，提取相关信息
for sline in blocks:
    start_t = time.time()
    i+=1
    tmp = []
    # print("sline:", sline[8],sline[18],sline[14], sline[19])
    # print("address:",sline[8])
    # 从当前行提取地址信息并分割（假设地址在第9列，索引8）
    t = sline[8].split(",")
    ##collect lat,lon
    #地理编码器（用于将地址转换为经纬度）
    geolocater = Nominatim(user_agent='demo_of_gnss_help')
    try:
        # 检查该地址是否已进行过地理编码
        if t[0] not in add_pos.keys():
            # print("not in here")
            # 对新地址进行地理编码获取经纬度
            location = geolocater.geocode(t[0])
            # 验证经纬度是否有效
            if hasattr(location,'latitude') and (location.latitude is not None) and hasattr(location,'longitude') and (location.longitude is not None):
                # print([location.latitude, location.longitude])
                # println()
                # print("t:", t)
                # tmp.append([location.latitude, location.longitude])
                # tmp.append(reg_nyc_dict[sline[18]])
                # 收集当前房产信息：建筑类别编码、土地面积、销售价格、总价
                add_pos[t[0]] = [location.latitude, location.longitude]
                tmp.append(reg_nyc_dict[sline[18]])
                tmp.append(sline[14])
                tmp.append(sline[19])
                # print("--:",float(sline[19])/float(sline[14]))
                tmp.append(float(sline[19]))

                # 将经纬度按建筑类别分组存储
                if reg_nyc_dict[sline[18]] not in region_f.keys():
                    region_f[reg_nyc_dict[sline[18]]] = []
                    region_f[reg_nyc_dict[sline[18]]].append([location.latitude, location.longitude])
                else:
                    region_f[reg_nyc_dict[sline[18]]].append([location.latitude, location.longitude])

                # 将当前房产处理结果加入总列表
                NYC_house_middle.append(tmp)
                
        else:
            # print("---in here---")
            # print("add_pos[t[0]]:", add_pos[t[0]])
            tmp.append(reg_nyc_dict[sline[18]])
            tmp.append(sline[14])
            tmp.append(sline[19])
            # print("--:",float(sline[19])/float(sline[14]))
            # tmp.append(float(sline[19]))
            if reg_nyc_dict[sline[18]] not in region_f.keys():
                region_f[reg_nyc_dict[sline[18]]] = []
                region_f[reg_nyc_dict[sline[18]]].append(add_pos[t[0]])
            else:
                region_f[reg_nyc_dict[sline[18]]].append(add_pos[t[0]])
            NYC_house_middle.append(tmp)

    # 处理地理编码过程中可能出现的错误
    except IOError:
        add_pos[t[0]] = []
        skip_num+=1
        # print('skip this row')

    # 打印当前处理的行数和耗时（用于监控进度）
    print("i:", i)
    print(time.time()-start_t) # 增加无效数据计数

print(region_f)    
print(NYC_house_middle[:3])
print(len(NYC_house_middle))
print(len(region_f))
print(len(add_pos))
print("skip_num",skip_num)

file=open(r"../data/NY_house.pickle","wb")
pickle.dump(NYC_house_middle,file) #storing_list
file.close()
file=open(r"../data/NY_stree_pos.pickle","wb")
pickle.dump(add_pos,file) #storing_list
file.close()

file=open(r"../data/NY_region.pickle","wb")
pickle.dump(region_f,file) #storing_list
file.close()

