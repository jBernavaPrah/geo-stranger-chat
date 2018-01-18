from config import configure_logger, create_app

configure_logger()
app = create_app()

# run the app.
if __name__ == "__main__":
	from controllers.resources.languages import check_language

	check_language()

	app.run(host='0.0.0.0', port=8080, threaded=True,
			# ssl_context='adhoc'
			)
