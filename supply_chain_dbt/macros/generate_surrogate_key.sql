/*
  Macro : generate_surrogate_key
  Usage  : Génère une clé surrogate cohérente à partir d'une liste de colonnes.
           Alternative portable à dbt_utils.generate_surrogate_key.
*/
{% macro generate_surrogate_key(field_list) %}
    {%- set fields = field_list | join(", ") -%}
    upper(convert(varchar(32), hashbytes('md5', concat({{ fields }})), 2))
{% endmacro %}