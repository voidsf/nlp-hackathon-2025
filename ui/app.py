from shiny import reactive
from shiny.express import input, render, ui

# setup
results = None
titles = None
timeline = None

ui.page_opts(fillable=True)

ui.h2("Dynamic UI")

with ui.div(id="main-content"):

    # input.<id> gets the value of the ui.____("<id>", "Text")

    with ui.layout_columns():
        ui.input_text("search", "Text input", "Enter text...")  

        @render.ui
        def slider_scale():

            value = f"{input.slider_select()}"
            max = 100

            if value == "Days":
                max = 100

            elif value == "Months":
                max = 12

            elif value == "Years":
                max = 5

            return ui.input_slider("slider", value, 0, max, max/2)
            
        ui.input_select(  
            "slider_select",  
            "Select an option below:",  
            {"Days": "Days", "Months": "Months", "Years": "Years"}
        )  

    with ui.div(id="titles-content"):
        pass

    with ui.div(id="timeline-content"):
        pass

    @reactive.effect
    def get_results():
        if input.search() != "Enter text...":
        
            # get results from API

            global results
            global titles
            results = []
            titles = [[1, "Trump Musk"], [2, "Trump"], [3,"Musk"], [4, "Tesla"]]

            if titles != None:
                ui.remove_ui("#titles")
                selector = ui.input_select("title_select", "Select an option below:", list_to_dict(titles)) 
                ui.insert_ui(
                    ui.div({"id": "titles"}, selector),
                    selector="#titles-content",
                    where="beforeEnd",
                )

    # timeline
    @reactive.effect
    def show_timeline():
        timeline = get_timeline_from_title(input.title_select())
        
        ui.h3("Timeline")
        with ui.layout_columns():
            for point in timeline:
                ui.remove_ui("#timeline")
            for point in timeline:
                ui.input_action_button(str(point[0]), point[1])
                card = ui.input_action_button(str(point[0]), point[1])
                ui.insert_ui(
                    ui.div({"id": "timeline"}, card),
                    selector="#timeline-content",
                    where="beforeEnd",
                )

    # text return
    @render.text
    def value():
        return input.text()

    # button
    # ui.input_action_button("btnl", "Trigger insert/remove ui")    
    

    # Another way of adding dynamic content is with ui.insert_ui() and ui.remove_ui().
    # The insertion is imperative, so, compared to @render.ui, more care is needed to
    # make sure you don't add multiple copies of the content.
    @reactive.effect
    def _():
        btn = input.btnl()
        if btn % 2 == 1:
            slider = ui.input_slider(
                "n2", "This slider is inserted with ui.insert_ui()", 0, 100, 20
            )
            ui.insert_ui(
                ui.div({"id": "inserted-slider"}, slider),
                selector="#main-content",
                where="beforeEnd",
            )
        elif btn > 0:
            ui.remove_ui("#inserted-slider")


def list_to_dict(array):

    this_dict = {}
    for x in array:
        this_dict[x[0]] = x[1]

    return this_dict

def get_timeline_from_title(title):
    # code here

    return [[1,"bbb"], [2,"musk leaves"], [3,"twitter"], [4,"stock drop"]]