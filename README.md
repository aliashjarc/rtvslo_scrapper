# rtvslo_scrapper - english version below
Web Scrapper komentarjev s poljubnih spletnih strani na rtvslo.si

Osnovna funkcija bo "potegnila" vse komentarje pod izbranimi novicami na spletnem portalu rtvslo.si ter jih shranila v .csv formatu. Trenutni atributi, ki jih funkcija izpiše se nanašajo na uporabniško ime, datum in čas komentarja ter komentar. Naknadno bi se glede na potrebo lahko dodalo še atribut "popularnosti", kjer bi potegnilo še število všečkov na komentar ali kaj podobnega. Za moje potrebe analize vsebine komentarjev se mi to ni zdelo smiselno.

Kodi so dodane tudi ostale funkcije, ki izboljšajo celotno izvedbo programa. Tako bo ime shranjene datoteke zapisano v formatu DD-MM-"prvih 10 znakov novice", kjer bodo šumniki pretvorjeni v njihove brezšumne alternative (c,s,z). Datum se določi glede na najpogostejši datum v DataFrame-u, kar bi morda pri novicah, ki so bile objavljene v časovnem intervalu med 11PM in 06AM (čas, ko je komentiranje onemogočeno) pomenilo, da se bo datum zamaknil za en dan. 

Časovni intervali: 
  - program ima 20 sekund časa, da locira gumb "prikaži komentarje", sicer sledi Timeout
  - program nato počaka 3 sekunde, da se vsi komentarji prikažejo
  - če locira komentarje, bo to izpisal v terminalu ter nadaljeval na naslednjo stran

X-Path za vse iskane atribute:
  - comment container (vsebuje podatke o posameznem komentarju; glej opombo spodaj): "//div[contains(@class, 'comment-container')]"
  - username: ".//a[@class='profile-name']"
  - timestamp: ".//span[@class='publish-meta']"
  - text: ".//p"

Opomba glede comment container: v izvirni kodi se nahajata dva različna comment container-ja - "comment-container" se nanaša na navaden komentar, medtem ko se "comment-container has-source" nanaša na komentarje, ki so nastali kot odgovor na nek že objavljen komentar. V kodi je tako vstavljeno tudi "varovalo", ki preveri, za kateri tip komentarja gre. 


# english version:
Web-scrapper of comments on rtvslo.si portal - government funded news portal in Slovenia. The program scrapes the comments and extracts the username, time, date and content of the comment under desired news article and stores them in .csv file. Furthermore, the program automatically names the file in DD-MM-"first 10 letters of the article" format and changes any non-ordinary letters of filename (e.g. č, š, ž) to their similar unicode letters (e.g. c, s, z). 
