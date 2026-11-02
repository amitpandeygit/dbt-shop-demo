{# The shop app stores money in paise (1 rupee = 100 paise). This turns paise into rupees. #}
{% macro paise_to_rupees(column_name, decimals=2) %}
    round({{ column_name }} / 100.0, {{ decimals }})
{% endmacro %}
