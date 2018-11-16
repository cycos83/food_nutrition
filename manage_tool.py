'''
DB 관리용 프로그램입니다.
DB에 식품 분류를 생성, 데이터 삽입이 가능합니다.
'''
import sqlite3
import xlrd
import pandas
import os
import re
from PIL import Image
from pyspark import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import udf, monotonically_increasing_id, lit
from pyspark.sql import Row

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('food.db')
        self.c = self.conn.cursor()

    def __del__(self):
        self.c.close()
        self.conn.close()

def init_db():
    try:
        db = Database()
        sql_file = open('food.sql').read()
        sqlite3.complete_statement(sql_file)
        db.c.executescript(sql_file)
        db.conn.commit()
        del db
    except Exception as e:
        print(e)
        print('Some error occured! fail!')
    else:
        print('Successfully initiatied!')

def data_insert():
    folder_path = input("Which folder do you want import?(eg. home/user): ")

    sheet_names = xlrd.open_workbook(folder_path+'/food_list.xlsx').sheet_names()

    print('I detected sheet names {0}.\n'
          'Do you want insert all or select specific sheet?\n'
          'If you want specific sheet, enter sheet name\n'
          'Other wise, JUST press enter only'.format(", ".join(sheet_names)))

    string = input()

    if string != '':
        if string not in sheet_names:
            print('Your input string not correct. exit')
            exit(1)
        else:
            sheet_names = [string]
            print('Only {0} sheet will be imported.'.format(string))

    print('Connecting to Spark. Wait few minute....')

    try:
        spark = SparkSession \
            .builder \
            .appName("input_data") \
            .config("spark.driver.class.path", "/home/jinho/PycharmProjects/food_nutrition/sqlite-jdbc-3.23.1.jar") \
            .config("spark.jars", "/home/jinho/PycharmProjects/food_nutrition/sqlite-jdbc-3.23.1.jar") \
            .getOrCreate()
    except Exception as e:
        print(e)
        print('Connecting Spark is fail! Some error ocurred! exit.')
        exit(1)

    print('Connecting to Spark success!')

    sc = spark.sparkContext
    sql_context = SQLContext(sc)

    data_schema = StructType([StructField('id', IntegerType(), True)
                                 , StructField('name', StringType(), True)
                                 , StructField('amount', FloatType(), True)
                                 , StructField('calorie', FloatType(), True)
                                 , StructField('carbohydrate', FloatType(), True)
                                 , StructField('fat', FloatType(), True)
                                 , StructField('protein', FloatType(), True)
                                 , StructField('natrium', FloatType(), True)
                                 , StructField('portion', FloatType(), True)])

    for sheet in sheet_names:
        all_data_frame = None
        all_ir_data_frame = None
        all_ir_mean_frame = None
        print('Merging {0} sheet....'.format(sheet))
        file = pandas.read_excel(folder_path+'/food_list.xlsx', sheet_name=sheet)
        pandas.DataFrame(file)
        file[['amount', 'calorie', 'carbohydrate', 'fat', 'protein', 'natrium', 'portion']] = \
        file[['amount', 'calorie', 'carbohydrate', 'fat', 'protein', 'natrium', 'portion']].astype(float)
        data_frame = spark.createDataFrame(file, schema=data_schema).withColumn('category', udf(lambda x: sheet)('id'))
        if all_data_frame is None:
            all_data_frame = data_frame
        else:
            all_data_frame = all_data_frame.union(data_frame)
        # ir data 처리
        for row in data_frame.collect():
            if os.path.exists('{0}/ir_data/{1}/{2}.xlsx'.format(folder_path, row['category'], row['id'])):
                try:
                    file = pandas.read_excel('{0}/ir_data/{1}/{2}.xlsx'.format(folder_path, row['category'], row['id']))
                    ir_data_frame = spark.createDataFrame(file)
                    range_value = 0
                    print('processing.... Do not exit. {0}'.format(row['id']))
                    id_category_data = [[row['id'], row['category']]]
                    rdd = sc.parallelize(id_category_data)
                    id_category = rdd.map(lambda x: Row(id=int(x[0]), category=str(x[1])))
                    id_category_frame = spark.createDataFrame(id_category)
                    ir_mean_list = []
                    for data in ir_data_frame.collect():
                        data = list(data)
                        ir_mean_list.append([sum(data)/len(data), range_value])
                        range_value += 1
                    rdd = sc.parallelize(ir_mean_list)
                    ir_mean_map = rdd.map(lambda x: Row(data=float(x[0]), range=int(x[1])))
                    ir_mean_frame = spark.createDataFrame(ir_mean_map)
                    ir_mean_frame = ir_mean_frame.crossJoin(id_category_frame)
                    if all_ir_mean_frame is None:
                        all_ir_mean_frame = ir_mean_frame
                    else:
                        all_ir_mean_frame = all_ir_mean_frame.union(ir_mean_frame)
                    '''
                    for data in ir_data_frame.collect():
                        data = list(data)
                        
                        #mean이 아닌 데이터 더하기 --> 너무 느림. 일단 웹 만들고 나중에 수정
                        rdd = sc.parallelize(data)
                        ir_value = rdd.map(lambda x: Row(data=float(x)))
                        ir_value_frame = spark.createDataFrame(ir_value)
                        ir_value_frame = ir_value_frame.crossJoin(id_category_frame) \
                                            .withColumn('round', monotonically_increasing_id()) \
                                            .withColumn('range', lit(counter))
                        if all_ir_data_frame is None:
                            all_ir_data_frame = ir_value_frame
                        else:
                            all_ir_data_frame = all_ir_data_frame.union(ir_value_frame)
                        
                        counter += 1
                        print(counter)
                    '''
                except Exception as e:
                    print(e)
                    print('ir_data read error. not included.')
        # list table에 import할 데이터
        all_data_frame.select('id', 'category', 'name').write.format('jdbc').mode('append'). \
            options(url='jdbc:sqlite:food.db', dbtable='list', driver='org.sqlite.JDBC').save()
        # information table에 import할 데이터
        all_data_frame.select('id', 'category', 'amount', 'calorie', 'carbohydrate', 'fat', 'protein', 'natrium',
                              'portion'). \
            write.format('jdbc').mode('append'). \
            options(url='jdbc:sqlite:food.db', dbtable='information', driver='org.sqlite.JDBC').save()
        all_ir_mean_frame.select('*').write.format('jdbc').mode('append'). \
            options(url='jdbc:sqlite:food.db', dbtable='ir_data_mean', driver='org.sqlite.JDBC').save()

    print('Data importing is done.')

def image_resize(path):
    print('now making.')
    dir_list_origin = os.listdir('original/'+path)
    basewidth = 500
    for i in dir_list_origin:
        if os.path.isdir('original/'+path+i):
            if not os.path.exists('resized/'+path+i):
                os.mkdir('resized/'+path+i)
            image_resize(path+i+'/')
        else:
            if re.match('^[^.].*\.jpg$', i):
                image = Image.open('original/'+path+i)
                size = image.size
                height = int(size[1] * basewidth/size[0])
                image.resize((basewidth, height)).save('resized/'+path+i)
    print('one folder done.')

if __name__ == '__main__':
    input_list = []
    print('Please Input command. 1 is insert_data(xlsx), 2 is init db. 3 is image-resize!')
    input_list.append(input())
    if input_list[0] == '1':
        data_insert()
    elif input_list[0] == '2':
        init_db()
    elif input_list[0] == '3':
        os.chdir('static/foods/images')
        image_resize('')
