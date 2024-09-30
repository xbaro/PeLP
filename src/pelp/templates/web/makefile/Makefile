APP_NAME:={{ app_name }}
LIB_NAME:=UOCContacts

OUT_APP:=bin
OUT_LIB:=lib

BUILDDIR_APP:=_build/app
app_sources:={% for dir in app.sources %}$(wildcard {{dir}}/*.c) {% endfor %}
app_objects:=$(addprefix $(BUILDDIR_APP)/, $(patsubst %.c, %.o, $(app_sources)))

{% for lib in libs %}
BUILDDIR_{{ lib.name|upper }}_LIB:=_build/lib
lib_{{ lib.name|lower }}_sources:={% for dir in lib.sources %}$(wildcard {{dir}}/*.c) {% endfor %}
lib_{{ lib.name|lower }}_objects:=$(addprefix $(BUILDDIR_{{ lib.name|upper }}_LIB)/, $(patsubst %.c, %.o, $(lib_{{ lib.name|lower }}_sources)))
{% endfor %}

$(BUILDDIR_APP)/%.o: %.c
        mkdir -p $(BUILDDIR_APP)/$(dir $^)
        gcc {% if use_valgrind %}-ggdb3 {% endif %}-c $^ -o $@ {% for lib in libs %}{% for dir in lib.include %}-I{{dir}} {% endfor %}{% endfor %}{% for dir in app.include %}-I{{dir}} {% endfor %}

{% for lib in libs %}
$(BUILDDIR_{{ lib.name|upper }}_LIB)/%.o: %.c
        mkdir -p $(BUILDDIR_{{ lib.name|upper }}_LIB)/$(dir $^)
        gcc {% if use_valgrind %}-ggdb3 {% endif %}-c $^ -o $@ {% for dir in lib.include %}-I{{dir}} {% endfor %}
{% endfor %}

all: $(OUT_APP)/$(APP_NAME)

{% for lib in libs %}
$(OUT_LIB)/lib{{ lib.name }}.a: $(lib_{{ lib.name|lower }}_objects)
        mkdir -p $(OUT_LIB)
        ar rcs $(OUT_LIB)/lib{{ lib.name }}.a $(lib_{{ lib.name|lower }}_objects)
{% endfor %}

$(OUT_APP)/$(APP_NAME): {% for lib in libs %}$(OUT_LIB)/lib{{ lib.name }}.a {% endfor %}$(app_objects)
        mkdir -p $(OUT_APP)
        gcc {% if use_valgrind %}-ggdb3 {% endif %}-lm -o $(OUT_APP)/$(APP_NAME) $(app_objects) -L$(OUT_LIB) {% for lib in libs %}-l{{ lib.name }} {% endfor %}

test: $(OUT_APP)/$(APP_NAME)
        make
        {% if use_valgrind %}valgrind --vgdb=no --leak-check=full --xml=yes --xml-file={{ valgrind_report }} --track-origins=yes --show-leak-kinds=all --keep-debuginfo=yes --fullpath-after=/code --show-error-list=yes {% endif %}$(OUT_APP)/$(APP_NAME) {{ test_args }}

clean:
        rm -Rf _build $(OUT_APP) $(OUT_LIB)
