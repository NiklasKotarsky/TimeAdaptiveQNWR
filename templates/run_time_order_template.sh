{% for path in paths -%}

    (cd {{path}}/Dirichlet; bash run.sh; cd ../../../../..) &
    (cd {{path}}/Neumann; bash run.sh; cd ../../../../..) &&
    cd {{path}}; bash run_relaxation.sh; cd ../../../../..;
    
{% endfor -%}
pwd