library(shiny)

ui <- fluidPage(
  h2("SYSEN 5381 - Posit Cloud Connect Demo"),
  p("Deployment successful!")
)

server <- function(input, output, session) {}

shinyApp(ui, server)
