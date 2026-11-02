{# Remove spaces at both ends and make the text lower case, so 'Pune ' and 'pune' match. #}
{% macro clean_text(column_name) %}
    lower(trim({{ column_name }}))
{% endmacro %}
