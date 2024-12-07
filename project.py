import os
import csv


class PriceMachine:
    """
    Класс, который загружает из указанного каталога найденные прайс-листы,
    а затем ищет по введенному слову необходимый  товар и выводит в формате html,
    найденную в прайс-листах информацию об этом товаре
    """
    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 0

    def load_prices(self, file_path='price'):
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии файлов.
        В файле ищет столбцы с названием товара, ценой и весом.
        """
        for filename in os.listdir(file_path):
            if 'price' in filename and filename.endswith('.csv'):
                filename_path = os.path.join(file_path, filename)
                with open(filename_path, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file, delimiter=',')
                    headers = next(reader)
                    product_col, price_col, weight_col = self._search_product_price_weight(headers)

                    for row in reader:
                        if len(row) > max(product_col, price_col, weight_col):
                            product = row[product_col].strip()
                            price = float(row[price_col].strip())
                            weight = float(row[weight_col].strip())
                            price_per_kg = price / weight if weight > 0 else 0
                            self.data.append({
                                'product': product,
                                'price': price,
                                'weight': weight,
                                'file': filename,
                                'price_per_kg': price_per_kg
                            })
        self.data.sort(key=lambda x: x['price_per_kg'])

    def _search_product_price_weight(self, headers):
        """
        Возвращает номера столбцов для продукта, цены и веса
        Допустимые названия для столбца с товаром:
            товар
            название
            наименование
            продукт

        Допустимые названия для столбца с ценой:
            розница
            цена

        Допустимые названия для столбца с весом (в кг.)
            вес
            масса
            фасовка
        """
        product_col = next(i for i, h in enumerate(headers) if h in ['название', 'продукт', 'товар', 'наименование'])
        price_col = next(i for i, h in enumerate(headers) if h in ['цена', 'розница'])
        weight_col = next(i for i, h in enumerate(headers) if h in ['фасовка', 'масса', 'вес'])
        return product_col, price_col, weight_col

    def export_to_html(self, fname='output.html'):
        """Экспорт выбранных данных(столбцов) из всех прайс-листов в html-файл"""
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for number, item in enumerate(self.data, start=1):
            result += f'''
                        <tr>
                            <td>{number}</td>
                            <td>{item['product']}</td>
                            <td>{item['price']}</td>
                            <td>{item['weight']}</td>
                            <td>{item['file']}</td>
                            <td>{item['price_per_kg']:.2f}</td>
                        </tr>
                    '''
        result += '''
                    </table>
                </body>
                </html>
                '''
        with open(fname, 'w', encoding='utf-8') as file:
            file.write(result)
        return f'Данные прайс-листов выгружены в {fname}'

    def find_text(self, text):
        """Получает текст и возвращает список позиций, содержащий этот текст в названии продукта"""
        found_items = [item for item in self.data if text.lower() in item['product'].lower()]
        return found_items


pm = PriceMachine()
pm.load_prices()

# Логика работы программы
while True:
    search_text = input('Введите текст для поиска (или "exit" для выхода): ')
    if search_text.lower() == "exit":
        print('Работа программы завершена.')
        break
    results = pm.find_text(search_text)
    if results:
        print(f'Найдено {len(results)} позиций:')
        for number, item in enumerate(results, start=1):
            print(f'{number}. {item["product"]} - {item["price"]} руб., {item["weight"]} кг., '
                  f'{item["file"]}, {item["price_per_kg"]:.2f} руб./кг.')
    else:
        print('По вашему запросу ничего не найдено.')

print('the end')
print(pm.export_to_html())
