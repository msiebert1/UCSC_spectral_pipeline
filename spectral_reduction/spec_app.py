import io
from base64 import b64encode

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


if __name__ == "__main__":
	buffer = io.StringIO()

	df = px.data.iris()
	fig = px.scatter(
	    df, x="sepal_width", y="sepal_length", 
	    color="species")
	fig.write_html(buffer)

	html_bytes = buffer.getvalue().encode()
	encoded = b64encode(html_bytes).decode()

	app = dash.Dash(__name__)
	app.layout = html.Div([
	    dcc.Graph(id="graph", figure=fig),
	    html.A(
	        html.Button("Download HTML"), 
	        id="download",
	        href="data:text/html;base64," + encoded,
	        download="plotly_graph.html"
	    )
	])

	app.run_server(debug=True)