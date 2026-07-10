/*
  Macro : date_key
  Usage  : Convertit une date en clé entière au format YYYYMMDD.
           Utilisé par les fact tables pour joindre dim_date.
  Exemple: {{ date_key('order_date') }} → 20150101
*/
{% macro date_key(date_column) %}
    cast(format({{ date_column }}, 'yyyyMMdd') as int)
{% endmacro %}