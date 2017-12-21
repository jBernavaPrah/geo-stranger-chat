# coding=utf-8
import telebot
import config
from controllers.resources.telegram_base import message_handler

telegram_it = telebot.TeleBot(config.TELEGRAM_KEY, threaded=False)
telegram_it.chat_type = 'telegram'
telegram_it.lang = 'it'
telegram_it.commands = {  # command description used in the "help" command
	'start': 'Inizia una conversazione con un nuovo GeoStrangers',
	'stop': 'Smetto di inviarti nuovi GeoStrangers',
	'delete': 'Elimina i tuoi dati dalla piattaforma GeoStranger',
	'terms': 'I termini di utilizzo del contratto',
	'notify': "C'è qualcosa che vuoi farmi notare? Qualche bug? Provvederò a innoltrarlo alle scimmie che mi hanno creato.",
	'help': 'Lista di tutti i comandi.',
}

telegram_it.error_message = "C'è stato un errore interno... :( Riprova.."
telegram_it.terms = ''

telegram_it.user_required_but_not_found = "Hmm... Non ti conosco.. Ma non importa :) Iniziamo! :) "

telegram_it.help_message = 'Di seguito i comandi che puoi utilizzare con il bot:'
telegram_it.stop_message = "Ok stoppato. Se vuoi reiniziare, basta che clicchi su /start ;)"
telegram_it.yes_message = 'Sì'
telegram_it.no_message = 'No'
telegram_it.delete_sure_message = "Sei sicuro di voler cancellarti?"
telegram_it.not_deleted_message = "Bene, non ho cancellato nulla."
telegram_it.delete_completed_message = "Ok, ho cancellato i tuoi dati. Ti ricordo che devi eliminare anche tutta la cronologia sul tuo cellulare.\n\n Mi dispiace che te ne vai.\nQuando vorrai tornare, inizia semplicemente con il tasto /start o scrivimi qualcosa! :)"
telegram_it.start_message = "Benvenuto \xF0\x9F\x98\x8B\xF0\x9F\x98\x8B!\n\nTra poco inizierai a chattare.\nContinuando con il bot accetti i termini e le condizioni che trovi su /terms.\nPotrai cancellarti in qualsiasi momento con il comando /delete.\n\n(La lista completa dei comandi la trovi su /help) \n\n Se sei d'accordo, iniziaimo! "
telegram_it.location_ask_message = 'Dove ti trovi?\n\n(Scrivi la tua città e la provincia o se sei con il cellulare inviami la posizione)'
telegram_it.location_ask2_message = 'Dove ti trovi? Cerca di aggiungere più informazioni (Città, Provincia, Stato)'
telegram_it.location_not_found_message = 'Non abbiamo trovato questa città. Riprova..'
telegram_it.location_error_message = "Non possiamo continuare se non mi invii la tua posizione. :( \n\n (Usa il tasto \xF0\x9F\x93\x8E -> \"Posizione\") \n\n La posizione non serve che sia esatta, puoi anche spostare il marker \xF0\x9F\x98\x84"
telegram_it.location_is_correct_message = "E' corretta questa posizione?\n\n {location_text}"
telegram_it.in_search_message = 'Inizio a cercare..'
telegram_it.sex_ask_message = 'Salvato :) Sei maschio o femmina?'
telegram_it.man_message = 'Maschio'
telegram_it.female_message = 'Femmina'
telegram_it.sex_error_message = 'Non capisco.. Seleziona se sei maschio o femmina'
telegram_it.completed_message = 'Bene! :) Abbiamo finito, ora iniziamo..\n\n Ti ricordo di non comportarti male.'
telegram_it.age_ask_message = "Bene, qual'è la tua età?"
telegram_it.age_error_message = 'Mandami solo il numero di anni :)'
telegram_it.found_new_geostranger_message = 'Super! Trovato il tuo GeoStranger, è {sex} ed ha {age} anni. Si trova a circa {distance} {unit_distance} da te. Ora tutti i messaggi che invierai a me verranno spediti al utente anonimo con cui stai chattando.'

message_handler(telegram_it)
