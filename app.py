from tools import database
from flask import Flask, render_template, url_for, request \
                    , send_file, Response, redirect, abort
import os
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    database.init_app(app)

    def sql_condition_generator(key_and, key_exactly, key_or, key_except, category):  # 일반 검색시 key_or, 나머지는 고급 검색에 사용된다.
        search_text = ''

        key_and = (lambda x: x.split() if x else None)(key_and)  #리스트
        key_exactly = (lambda x: x if x else None)(key_exactly)  #스트링
        key_or = (lambda x: x.split() if x else None)(key_or)  #리스트
        key_except = (lambda x: x.split() if x else None)(key_except)  #리스트
        category = (lambda x: x if x else None)(category)

        if key_and:
            and_text = ''
            for n in range(len(key_and)):
                and_text += 'name like "%' + key_and[n] + '%"'
                if n != len(key_and) - 1:
                    and_text += ' and '
        else:
            and_text = None

        if key_exactly:
            exactly_text = 'name like "%' + key_exactly + '%"'
        else:
            exactly_text = None

        if key_or:
            or_text = ''
            for n in range(len(key_or)):
                or_text += 'name like "%' + key_or[n] + '%"'
                if n != len(key_or) - 1:
                    or_text += ' or '
        else:
            or_text = None

        if key_except:
            except_text = ''
            for n in range(len(key_except)):
                except_text += 'name not like "%' + key_except[n] + '%"'
                if n != len(key_except) - 1:
                    except_text += ' and '
        else:
            except_text = None

        if category:
            category_text = 'list.category = "' + category + '"'
        else:
            category_text = None

        text_list = []

        for text in (and_text, exactly_text, or_text, except_text, category_text):
            if text:
                text_list.append(text)

        for n in range(len(text_list)):
            search_text += '(' + text_list[n] + ')'
            if n != len(text_list) - 1:
                search_text += ' and '

        print(search_text)

        #sql_text = 'SELECT * FROM list WHERE ' + search_text

        return search_text


    @app.route('/images/<path:image_name>')  # 음식 이미지 라우팅
    def get_image(image_name):
        if os.path.exists('static/foods/images/resized/'+image_name):
            return send_file('static/foods/images/resized/'+image_name)
        else:
            return send_file('static/img/no_image_avail.png')


    @app.route('/')  # 메인 화면입니다.
    def main_page():
        return render_template('main.html')


    @app.route('/search', methods=['get'])  # 검색 결과화면입니다.
    def search(advanced_search_text=None):
        db = database.get_db()

        if request.args.get('page_number'):
            page_number = int(request.args.get('page_number'))
        else:
            page_number = 1

        sql_condition = sql_condition_generator(request.args.get('key_and'), request.args.get('key_exactly'), request.args.get('key_or'), request.args.get('key_except'), request.args.get('category'))

        count_sql_text = 'SELECT COUNT(*) FROM list JOIN information on list.category = information.category and list.id = information.id'
        if sql_condition:
            count_sql_text += ' WHERE '

        amount_number = db.execute(count_sql_text + sql_condition).fetchone()['count(*)']

        last_page_number = int(amount_number / 30) + 1
        print('lalalala' + str(last_page_number))

        sql_text = 'SELECT * FROM list JOIN information on list.category = information.category and list.id = information.id'
        if sql_condition:
            sql_text += ' WHERE '

        foods = db.execute(sql_text + sql_condition + ' LIMIT ' + str((page_number - 1)*30) + ',30').fetchall()

        foods = list(foods)
        none_list = []

        foods_with_none_data = []

        for food_n in range(len(foods)):
            if foods[food_n]['calorie'] is None:
                foods_with_none_data.append(foods[food_n])
                none_list.append(food_n)

        for n in range(len(none_list)):
            foods.pop(none_list[n] - n)
        print(len(foods))
        foods += foods_with_none_data
        print(len(foods))

        return render_template('search.html', key_and=request.args.get('key_and'), key_exactly = request.args.get('key_exactly'), key_or = request.args.get('key_or'), key_except = request.args.get('key_except'), foods=foods, this_page_number=page_number, last_page_number=last_page_number)


    @app.route('/advanced_search', methods=['get'])  # 고급 검색 화면
    def advanced_search():
        return render_template('advanced_search.html')


    @app.route('/food_information', methods=['get'])
    def food_information():
        db = database.get_db()
        food_info = db.execute('SELECT * FROM information WHERE id = ? and category = ?',
                               (request.args.get('food_id'), request.args.get('food_category'))).fetchone()

        return render_template('food_information.html', food_info=food_info, food_name=request.args.get('food_name'))


    # ir 서치 및 그래프 작성 불량 입력값 확인
    def is_valid_for_ir(value_max, value_min, range_max, range_min):
        if value_max < value_min:
            return False
        if range_max < range_min:
            return False
        if True in (value_max < 0, value_min < 0, range_max < 0, range_min < 0):
            return False
        return True


    @app.route('/ir_search', methods=['get'])
    def ir_search():
        if not is_valid_for_ir(int(request.args.get('value_max')), int(request.args.get('value_min')), int(request.args.get('range_max')), int(request.args.get('range_min'))):
            return error_page('not valid')

        db = database.get_db()
        sql_condition = sql_condition_generator(request.args.get('key_and'), request.args.get('key_exactly'),
                                                request.args.get('key_or'), request.args.get('key_except'), request.args.get('category'))

        sql_text = 'SELECT name, id, category FROM list'
        if sql_condition:
            sql_text += ' WHERE '

        foods = db.execute(sql_text + sql_condition).fetchall()

        selected_name = request.args.get('selected_name')

        selected_food = db.execute('SELECT * FROM list JOIN information i on list.category = i.category and list.id = i.id WHERE name=?',
                                   (selected_name,)).fetchone()

        return render_template('ir_search.html', foods=foods, key_and=request.args.get('key_and'), key_exactly=request.args.get('key_exactly'),
                               key_or=request.args.get('key_or'), key_except=request.args.get('key_except'), category=request.args.get('category'),
                               selected_name=selected_name, selected_food=selected_food, range_max=request.args.get('range_max'), range_min=request.args.get('range_min'),
                               value_max=request.args.get('value_max'), value_min=request.args.get('value_min'))


    @app.route('/plot.png', methods=['get'])
    def plot_png():
        if not is_valid_for_ir(int(request.args.get('value_max')), int(request.args.get('value_min')), int(request.args.get('range_max')), int(request.args.get('range_min'))):
            return error_page('not valid')
        db = database.get_db()
        subject = request.args.get('subject')
        selected_name = request.args.get('selected_name')
        if selected_name == 'None':
            selected_name = None
        range_max = request.args.get('range_max')
        range_min = request.args.get('range_min')
        value_max = request.args.get('value_max')
        value_min = request.args.get('value_min')

        sql_condition = sql_condition_generator(request.args.get('key_and'), request.args.get('key_exactly'),
                                                request.args.get('key_or'), request.args.get('key_except'), request.args.get('category'))
        sql_text = 'SELECT category, id, name FROM list'
        if sql_condition:
            sql_text += ' WHERE '

        category_and_id = db.execute(sql_text + sql_condition).fetchall()

        other_ir_data = []

        selected_ir_data = None

        for food in category_and_id:
            if (selected_name is not None) and food['name'] == selected_name:
                selected_ir_data = db.execute('SELECT data FROM ir_data_mean WHERE category = ? '
                                              'and id = ?',
                                              (food['category'], food['id'])).fetchall()

            else:
                other_ir_data.append(db.execute('SELECT data FROM ir_data_mean WHERE category = ? '
                                                'and id = ?',
                                              (food['category'], food['id'])).fetchall())

        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)

        if (selected_name is not None) and (selected_ir_data is not None):
            for data in other_ir_data:
                axis.plot(data, color='Gray')
            axis.plot(selected_ir_data, linewidth=5, color='Red')
        else:
            for data in other_ir_data:
                axis.plot(data)

        axis.set_xlabel('Wave length (nm)')
        axis.set_ylabel('Reflectance')

        axis.set_xlim(int(range_min), int(range_max))
        axis.set_ylim(int(value_min), int(value_max))

        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)

        return Response(output.getvalue(), mimetype='image/png')

    @app.route('/docs')
    def docs_list():
        docs = os.listdir('static/docs')

        return render_template('docs.html', docs=docs)

    @app.route('/docs/<path:file_name>')
    def doc_download(file_name):
        if not os.path.exists('static/docs/' + file_name):
            abort(404)

        return send_file('static/docs/' + file_name)

    @app.route('/error')
    def error_page(error):
        return render_template('error.html', error=error)

    return app
