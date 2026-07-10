/*
  Macro : kpi_otif
  Usage  : Calcule l'indicateur OTIF (On-Time In-Full).
           1 si livré à temps ET commande complète, 0 sinon.
*/
{% macro kpi_otif(days_real, days_scheduled, order_status) %}
    case
        when {{ days_real }} <= {{ days_scheduled }}
         and {{ order_status }} = 'COMPLETE' then 1
        else 0
    end
{% endmacro %}