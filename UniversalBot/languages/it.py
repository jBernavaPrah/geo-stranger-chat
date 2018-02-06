# coding=utf-8
from flask import url_for

lang = {
		'command_start': '/start Se non sei registrato, ti registro nella nostra piattaforma.',
		'command_stop': u'/stop Ti disconnetto dalla conversazione corrente e non ti invio altri GeoStrangers',
		'command_delete': '/delete Elimino tutti i dati dalla mia memoria',
		'command_terms': '/terms Link ai termini di utilizzo',
		'command_notify': "/notify Vuoi che invio un messaggio ai miei creatori? Hai trovato un bug o qualcosa da migliorare? Scrivimelo.",
		'command_help': '/help La lista dei miei Comandi',
		'error': "OPSSS.. Errrore interno..\n\nHo provveduto ad inviare questo errore ai miei creatori.",
		'terms': 'Trovi i termini del servizio sul nostro sito: %s' % url_for('index.terms_page', _external=True),
		'user_required_but_not_found': "Opss... Non so chi sei! hahaha :)",

		'help': 'Io ti posso aiutare a trovare nuovi amici vicino a te. \nUna volta completata la fase iniziale potrai effettuare la ricerca di un nuovo GeoStranger cliccando su /search. Se durante la chat mi invii di nuovo /search, provvederò a cercarti un nuovo GeoStranger.\nPer non ricevere altri GeoStranger usa il comando /stop. \n\n*Lista dei comandi che mi puoi inviare:*\n\n{help_text}',

		'ask_stop_sure': 'Sei sicuro di non voler più ricevere nuovi GeoStranger?',
		'ask_stop_also_current_chat': 'Sei sicuro di non voler più ricevere nuovi GeoStranger?\n\nSe continui, ti disconnetterai dalla chat corrente.',
		'not_stopped': 'Ok, non fermato.',

		'stop': "*Fermato*.\n\nPer cercare un nuovo Geostranger usa il comando /search",

		'yes': 'Sì',
		'no': 'No',
		'ask_delete_sure': "*Sei sicuro di voler eliminare tutti i tuoi dati?*\n\nQuesta operazione è irreversibile.",
		'not_deleted': "Bene, *non ho cancellato nulla*.",
		'delete_completed': "*Ho cancellato i tuoi ID dai miei dati.* Ti ricordo di eliminare la cronologia dal tuo telefono!\n\nSe vuoi puoi iniziare di nuovo a scrivermi o utilizza il comando /start.",

		'welcome': "*Benvenuto GeoStranger!* \U0001F600\U0001F600!\n\nSe risponderai alle mie domande, accetti i termini (%s) dei miei creatori.\nPotrai eliminarti dalla mia memoria in qualsiasi momento con il comando /delete.\n\nLa lista completa dei comandi la trovi con il comando /help." % url_for(
			'index.terms_page', _external=True),

		'ask_location': 'Da dove mi scrivi?\n\nPuoi scrivermi il nome della tua città (Nome città, Regione, Stato)',
		're_ask_location': 'Da dove mi scrivi?',
		'location_not_found': "Non ho trovato {location_text}. Scrivi un'altra città o inviami la posizione se il tuo dispositivo lo permette..",
		'location_error': "Non possiamo continuare se non mi invii la tua posizione. :(",
		'ask_location_is_correct': "E' corretta la seguente posizione? \n\n{location_text}",
		'location_saved': 'Ok, ho salvato *{location_text}* come tua posizione.\n\nIn futuro puoi cambiarlo con il comando /location.',

		'search': 'Per iniziare una nuova chat usa il comando /search.\n\nTrovi la lista di tutti i comandi qui: /help.',
		'in_search': 'Ho iniziato a cercare...',

		'ask_sex': "Qual'è il tuo sesso?",
		'man': 'Maschio',
		'female': 'Femmina',
		'sex_error': 'Usa i bottoni (Maschio / Femmina).',

		'ask_age': "Adesso, quanti anni hai?",
		'age_error': "Scusami, ma non ho capito, Quanti anni hai?",
		'age_error_to_low': "Ci sono ti tuoi genitori con te? I miei creatori non sono felici se sei da solo. Chiedi ad un tuo genitore di stare con te.",
		'age_error_to_high': "Veramente hai {age} anni?? \n\nLo salverò, potrai cambiarlo piú avanti.",

		'completed': 'Ok! :) Abbiamo finito.\n\nUsa il comando /search per cercare un nuovo GeoStranger vicino a te!',

		'found_new_geostranger_first_time': 'Super! Ti ho trovato il tuo GoeStranger, vicino a *{location_text}*. Ora tutti i messaggi, video, immagini o audio che invierai a me verranno inoltrati in automatico a lui in modo anonimo.',
		'found_new_geostranger': 'Nuova chat con un utente che si trova a *{location_text}*.',

		'ask_notify': 'Ok, scrivi ora. :) La invierò immediatamente ai miei sviluppatori!',
		'notify_sent': 'Notifica inviata!',
		'go_to_real_geostranger_account': 'Ciao, questo bot è solo un alias. Utilizza invece @GeoStrangerBot. Grazie.',

		'conversation_stopped_by_other_geostranger': 'Geostranger disconnesso. \n\nPer iniziare usa il comando /search',

		'thanks': 'Grazie.',

		'play_audio': "GeoStranger ti ha inviato un audio. Clicca sul link per ascoltarlo:\n\n{url}",
		'play_video': 'GeoStranger ti ha inviato un video. Clicca sul link per visualizzarlo\n\n{url}',
		'download_file': 'GeoStrager ti ha inviato un documento. Clicca sul link per effettua il download:\n\n{url}',

		'not_compatible': 'Il messaggio non è compatibile. Non verrà inviato al GeoStranger.',

		'sure_search_new': 'Sicuro di voler fermare questa chat e cercare un nuovo GeoStranger?',

		'command_not_found': 'Non ho un comando che si chiama {command_text}. Per vedere tutti i comandi mandami /help.',

		}
