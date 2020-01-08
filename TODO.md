# Bugfixes

- Write collision with Playback
  - Potentielle Loesung muss man die Devices in das Actor System einbinden? -> Message serialization
- Catch too long URIs
- Waehrend URI translation kommt manchmal "E1" Fehler (lange URI Translation -> Frontendactor laeuft Amok?)
  - Potentielle Loesung: Polle nicht wahrend URI resolution (self.parent.tell(uri) ->  self.parent.tell(uri).get())
- Manchmal unkontrollierte Restarts (wahrscheinlich: Reader behauptet zwischendurch kein Tag zu sehen)
   - Potentielle Loesung: Verifiziere None read mit nochmal lesen

# QA stuff

- Add license file
- Write the readme
- Write some documentation, at least for major classes and design decisions
- Command helpstrings
- Stelle auf setup.cfg um
- Logging!

# Features

- ResumePolicy with PersistentDict
  - Was fuer Daten kann man bei PLaylists heranziehen. tracks sind denke ich einfach.
- Configuration for RC522 (antennaGain, GPIO pins)
- Konfigurierbares Pollinginterval

# Devices

- RC522UART hack
- RDM6300
