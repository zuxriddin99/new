from django import template
from django.utils.safestring import mark_safe
from mainapp.models import Smartphone

register = template.Library()

TABLE_HEAD = """
        <table class="table">
            <tbody>
            """

TABLE_TAIL = """
            </tbody>
        </table>
            """

TABLE_CONTENT = """
            <tr>
                <td>{name}</td>
                <td>{value}</td>
            </tr>
                """
PRODUCT_SPEC = {
    'notebook':{
        'Диагоналы': 'diagonal',
        'Тип дисплея': 'display_type',
        'Частота просессора': 'processor_freq',
        'РАМ': 'ram',
        'Видеокарта': 'video',
        'Время работы аккумулятора': 'time_widhout_charge'
    },
    'smartphone':{
        'Диагоналы': 'diagonal',
        'Тип дисплея': 'display_type',
        'Разррешение екрана': 'resolution',
        'Заряд аккумулятора': 'accum_volume',
        'РАМ': 'ram',
        'Наличие слота для SD карты': 'sd',
        'Максимальный объем SD карты': 'sd_volume_max',
        'Камера (МП)': 'main_cam_up',
        'фронталъная камера (МП)': 'frontal_cam_up'
    }
}
def get_product_spec(product, model_name):
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    return table_content

@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    if isinstance(product, Smartphone):
        if not product.sd:
            PRODUCT_SPEC['smartphone'].pop('Максимальный объем SD карты')
        else:
            PRODUCT_SPEC['smartphone']['Максимальный объем SD карты'] = 'sd_volume_max'
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)
