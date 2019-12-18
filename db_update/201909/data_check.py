import pandas as pd
import os
import numpy as np

# 숫자와 카테고리 이름 매칭에 따른 리스트 생성
categorys = ["", "seasoned_foods", "noodles", "egg_included_processed_products", "edible_oil_and_fat", "rice_cake", "tofu_or_jellied_foods", "meat", "special_purpose_food", "fish_meat_processed_products", "confectionery_frozen_dessert", "instant_food", "beverages"]

# # 이미지에 (2) 들어간 녀석 있나 찾기
# folders = ["exterior", "interior"]
# for folder in folders:
# 	files = os.listdir(folder)
# 	for file in files:
# 		if "(2)" in file:
# 			print(file)

for category in categorys:
	try:
		# 규칙에 맞춰 정리한 food_list 엑셀을 읽어서 값들을 입력한다.
		# 2018년과 비교해 전부 신규 카테고리이기 때문에 id 신경쓰지 않고 그냥 입력
		excel_data = pd.read_excel("201909_food_list_v2.xlsx", sheet_name=category)
		excel_data2 = excel_data.where((pd.notnull(excel_data)), None)

		for index, row in excel_data2.iterrows():
			try:
				pid = row['pid'].strip()
				# 외부이미지 체크
				if not os.path.exists("exterior/" + pid + ".jpg"):
					print(pid, "no exterior image")

				# 내부이미지 체크
				if not os.path.exists("interior/" + pid + ".jpg"):
					print(pid, "no interior image")

				# ir데이터 체크, 9번 항목은 9.xlsx에 몰려있음
				category = pid.split("-")[0]
				ir_data = None
				if category == "9":
					try:
						ir_data = pd.read_excel("ir_data/9.xlsx", sheet_name=pid)
					except Exception as e:
						print(pid, "no ir data")
				else:
					if not os.path.exists("ir_data/" + pid + ".xlsx"):
						print(pid, "no ir data")
					else:
						ir_data = pd.read_excel("ir_data/" + pid + ".xlsx")

				if not ir_data is None:
					if len(ir_data.columns) != 5:
						print(pid, "ir data col error", ir_data.columns)
					else:
						for col in ir_data:
							for idx in range(256):
								if ir_data.iloc[idx][col] is None:
									print(pid, "ir data None", col)

			except Exception as e:
				print("ERROR:", pid, e)

	except Exception as e:
		print(category, e)