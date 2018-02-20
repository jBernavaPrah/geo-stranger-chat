from flask_babel import gettext

messages_to_not_botting = ['yes', 'no']

bot_messages = {
	"ask_delete_sure": gettext(
		"*Are you sure to delete all your data and stop talk with other GeoStrangers?*\n\nYou cannot undo anymore."),
				"ask_location": gettext("From where you write me?\n\nEnter the name of City and Region."),
				"ask_location_is_correct": gettext("Is correct this position?\n\n%(location_text)s"),
	"notification": gettext("To sent a notification, open this link:\n\n%(contact_us_url)s"),
				"ask_sex": gettext("What your gender?"),
	"ask_stop_also_current_chat": gettext(
		"Are you sure to stop receiving new GeoStranger?\n\nThis will stop also current chat."),
				"ask_stop_sure": gettext("Are you sure to stop receiving new GeoStranger?"),
				"attachment_not_compatible":gettext("Sorry I cannot sent one or more of your attachments. You can only sent %(allowed_attachments)s."),
				"command_new": gettext("Start new conversation and stop any current conversation."),
				"command_location": gettext("Change your location."),
				"command_delete": gettext("Delete your data from GeoStranger datacenters."),
				"command_help": gettext("Bot Commands."),
	"command_not_found": gettext("I not have this command: %(command_text)s. To see all command send me */help*."),
	"command_notify": gettext(
		"There are some information that my creators need to know? Or you found a Bug? Send to me."),
				"command_start": gettext("Start new conversation with GeoStrangers or registry to our platform."),
				"command_stop": gettext("Stop receiving GeoStrangers messages."),
				"command_terms": gettext("Show Our Terms."),
	"completed": gettext("We have finish.\n\nNow use */new* to start talk and found new friends!"),
	"conversation_stopped_by_other_geostranger": gettext(
		"Geostranger disconnected.\n\nBe patient, new chat partner will came shortly."),
	"delete_completed": gettext(
		"I have deleted all association of you in our data. Remember to delete also this chat.\n\nTo restart, send me a message or use command */start*."),
	"download_file": gettext("GeoStranger have sent a document. Click link to download it:\n\n%(file_url)s"),
	"download_attachment_error": gettext(
		"Sorry, I cannot sent this attachment to your chat partner :( \n\nTry different file.\n(My developers are working on this issue.)"),
				"error": gettext("Internal error. Retry later..\n\nPS. I have reported this case to my creators."),
				"female": gettext("Female"),
	"found_new_geostranger": gettext("New GeoStranger, near *%(location_text)s*. Use */new* to start new chat."),
	"found_new_geostranger_first_time": gettext(
		"Super! I have found your GeoStranger, near *%(location_text)s*. Now, all message, video, image or audio will be sent directly to this GeoStranger in anonymously mode. (Use */stop* to stop receiving new GeoStrangers)"),
				"new_chat": gettext('== New Chat =='),
	"go_to_real_geostranger_account": gettext("Hi. This is only an alias. Use @GeoStrangerBot instead. Thanks."),
	"help": gettext(
		'Hi GeoStranger! My work is to find new strangers near you!\n\nOnce you have completed the initial phase you can search for a new GeoStranger by sending command */new*. If you send me */new*, during the chat, I will look for you to find a new GeoStranger.\nTo not receive other GeoStranger send me the */stop* command.'),
				"in_search": gettext("I have start searching.."),
	"location_error": gettext("I cannot continue if you not send me your position. What is your current location?"),
	"location_not_found": gettext("I haven't found %(location_text)s. Retry with other city or be more specific.."),
	"location_saved": gettext(
		"Ok, I have saved *%(location_text)s* location.\n\nTo change it, use command */location*."),
				"man": gettext("Male"),
				"no": gettext("No"),
	"not_compatible": gettext("I cannot understand that message sorry :( It will not be sent to GeoStranger."),
				"not_deleted": gettext("Good, *I haven't delete anythings*"),
				"not_stopped": gettext("Ok, not stopped."),
				"notify_sent": gettext("Notify sent!"),
				"play_audio": gettext("GeoStranger have sent an audio. Click link to play it:\n\n%(file_url)s"),
				"play_video": gettext("GeoStranger have sent a video. Click link to play it:\n\n%(file_url)s"),
				"re_ask_location": gettext("Then, what is your current location?\n\n"),
	"search": gettext("To start new chat send me command */new*.\n\nList of all commands */help*."),
	"search_not_found": gettext("All users are now in talk. Be patient, you will be the first that will be mached."),
				"sex_error": gettext("Use buttons. Select only if you are male or female."),
	"show_image": gettext("GeoStranger have sent a image. Click link to see it:\n\n%(file_url)s"),
	"show_file": gettext("GeoStranger have sent an attachment. Click link to see it:\n\n%(file_url)s"),
	"stop": gettext("*Stopped*.\n\nTo restart press */new*"),
				"sure_search_new": gettext("Sure to stop this chat and search new GeoStranger?"),
				"terms": gettext("Find our terms here: %(terms_url)s"),
	"commands_available": gettext("Commands available: %(commands)s"),
				"thanks": gettext("Thanks."),
	"user_required_but_not_found": gettext(
		"Hmm how are you?? haha I don't know you, but this is not important, we can start now! :)"),
				"welcome": gettext("*Welcome GeoStranger!*"),
				"yes": gettext("Yes")}
