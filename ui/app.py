from shiny import reactive
from shiny.express import input, render, ui
import asyncio

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
    async def get_results():
        if input.search() != "Enter text...":
        
            with ui.Progress(min=1, max=15) as p:
                p.set(message="Calculation in progress", detail="This may take a while...")

                for i in range(1, 15):
                    p.set(i, message="Computing")
                    await asyncio.sleep(0.1)

            ui.remove_ui("#value")

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

    with ui.layout_columns():
        with ui.card():
            "Card 1"
        with ui.card():
            "Card 2"
        with ui.card():
            "Card 3"
            
    # text return
    @render.text
    def value():
        return input.text()
    
    

    # button
    # ui.input_action_button("btnl", "Trigger insert/remove ui")    



def list_to_dict(array):

    this_dict = {}
    for x in array:
        this_dict[x[0]] = x[1]

    return this_dict

def get_timeline_from_title(title):
    # code here

    return [[1,"bbb"], [2,"musk leaves"], [3,"twitter"], [4,"stock drop"]]