import requests
import time
import json
import os
import io
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pypdf import PdfReader
from groq import Groq

# ============================================================
# CONFIG
# ============================================================

WATCHLIST = [
"20MICRONS","21STCENMGM","360ONE","3BBLACKBIO","3IINFOLTD","3MINDIA","3PLAND","5PAISA","63MOONS",
"A2ZINFRA","AAATECH","AADHARHFC","AAKASH","AAREYDRUGS","AARNAV","AARON","AARTECH","AARTIDRUGS",
"AARTIIND","AARTIPHARM","AARTISURF","AARVI","AAVAS","ABANSENT","ABB","ABBOTINDIA","ABCAPITAL",
"ABCOTS","ABDL","ABFRL","ABINFRA","ABLBL","ABMINTLLTD","ABMKNO","ABREL","ABSLAMC","ACC",
"ACCELYA","ACCURACY","ACE","ACEINTEG","ACI","ACL","ACMESOLAR","ACSTECH","ACUTAAS","ADANIENSOL",
"ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ADFFOODS","ADL","ADOR","ADROITINFO","ADSL",
"ADVAIT","ADVANCE","ADVANIHOTR","ADVENTHTL","ADVENZYMES","AEGISLOG","AEGISVOPAK","AEPL","AEQUS",
"AEROENTER","AEROFLEX","AERONEU","AETHER","AFCONS","AFFLE","AFFORDABLE","AFIL","AFSL","AGARIND",
"AGARWALEYE","AGI","AGIIL","AGRITECH","AGROPHOS","AHCL","AHLADA","AHLEAST","AHLUCONT","AHLWEST",
"AIAENG","AIIL","AIRAN","AIROLAM","AJANTPHARM","AJAXENGG","AJMERA","AJOONI","AKASH","AKCAPIT",
"AKG","AKI","AKSHAR","AKSHARCHEM","AKSHOPTFBR","AKUMS","ALANKIT","ALBERTDAVD","ALEMBICLTD",
"ALGOQUANT","ALICON","ALIVUS","ALKALI","ALKEM","ALKYLAMINE","ALLCARGO","ALLDIGI","ALLTIME",
"ALMONDZ","ALOKINDS","ALPA","ALPHAGEO","AMAGI","AMANTA","AMBALALSA","AMBER","AMBICAAGAR",
"AMBIKCO","AMBUJACEM","AMDIND","AMIRCHAND","AMJLAND","AMNPLST","AMRUTANJAN","ANANDRATHI",
"ANANTRAJ","ANDHRAPAP","ANDHRSUGAR","ANGELONE","ANIKINDS","ANKITMETAL","ANMOL","ANSALAPI",
"ANTELOPUS","ANTGRAPHIC","ANTHEM","ANUHPHR","ANUP","ANURAS","APARINDS","APCL","APCOTEXIND",
"APEX","APLAPOLLO","APLLTD","APOLLO","APOLLOHOSP","APOLLOPIPE","APOLLOTYRE","APOLSINHOT",
"APTECHT","APTUS","AQYLON","ARCHIDPLY","ARCHIES","ARE&M","ARENTERP","ARFIN","ARIES","ARIHANT",
"ARIHANTCAP","ARIHANTSUP","ARIS","ARKADE","ARMANFIN","AROGRANITE","ARROWGREEN","ARSHIYA",
"ARSSBL","ARTEMISMED","ARTNIRMAN","ARVEE","ARVIND","ARVINDFASN","ARVSMART","ASAHIINDIA",
"ASAHISONG","ASAL","ASALCBR","ASHAPURMIN","ASHIANA","ASHIKA","ASHIMASYN","ASHOKA","ASHOKAMET",
"ASHOKLEY","ASIANENE","ASIANHOTNR","ASIANPAINT","ASIANTILES","ASKAUTOLTD","ASMS","ASPINWALL",
"ASTAR","ASTEC","ASTERDM","ASTRAL","ASTRAMICRO","ASTRAZEN","ASTRON","ATALREAL","ATAM","ATGL",
"ATHERENERG","ATL","ATLANTAA","ATLANTAELE","ATLASCYCLE","ATUL","ATULAUTO","AUBANK","AURIGROW",
"AURIONPRO","AUROPHARMA","AURUM","AUSOMENT","AUTOAXLES","AUTOIND","AVADHSUGAR","AVALON",
"AVANTEL","AVANTIFEED","AVG","AVL","AVONMORE","AVROIND","AVTNPL","AWFIS","AWHCL","AWL",
"AXISBANK","AXISCADES","AXITA","AYE","AYMSYNTEX","AZAD","BAFNAPH","BAGFILMS","BAIDFIN",
"BAJAJ-AUTO","BAJAJCON","BAJAJELEC","BAJAJFINSV","BAJAJHCARE","BAJAJHFL","BAJAJHIND",
"BAJAJHLDNG","BAJAJINDEF","BAJAJST","BAJEL","BAJFINANCE","BALAJEE","BALAJITELE","BALAMINES",
"BALAXI","BALKRISHNA","BALKRISIND","BALMLAWRIE","BALPHARMA","BALRAMCHIN","BALUFORGE",
"BANARBEADS","BANARISUG","BANCOINDIA","BANDHANBNK","BANG","BANKA","BANKBARODA","BANKINDIA",
"BANSALWIRE","BANSWRAS","BASF","BASML","BATAINDIA","BATLIBOI","BAYERCROP","BBL","BBOX","BBTC",
"BBTCL","BCG","BCLIND","BCONCEPTS","BCPL","BDL","BEARDSELL","BECTORFOOD","BEDMUTHA","BEEKAY",
"BEL","BELLACASA","BELRISE","BEML","BENGALASM","BEPL","BERGEPAINT","BESTAGRO","BETA","BFINVEST",
"BFUTILITIE","BGRENERGY","BHAGCHEM","BHAGERIA","BHAGYANGR","BHANDARI","BHARATCOAL","BHARATFORG",
"BHARATGEAR","BHARATRAS","BHARATSE","BHARATWIRE","BHARTIARTL","BHARTIHEXA","BHEL","BI","BIGBLOC",
"BIKAJI","BIL","BILVYAPAR","BIMETAL","BIOCON","BIOFILCHEM","BIRLACABLE","BIRLACORPN",
"BIRLAMONEY","BIRLANU","BIRLAPREC","BLACKBUCK","BLACKROSE","BLAL","BLBLIMITED","BLIL","BLISSGVS",
"BLKASHYAP","BLS","BLSE","BLUECOAST","BLUEDART","BLUEJET","BLUESTARCO","BLUESTONE","BLUSPRING",
"BMWVENTLTD","BNAGROCHEM","BNALTD","BODALCHEM","BOHRAIND","BOMDYEING","BONLON","BORANA",
"BOROLTD","BORORENEW","BOROSCI","BOSCH-HCIL","BOSCHLTD","BPCL","BPL","BRIGADE","BRIGHOTEL",
"BRITANNIA","BRNL","BROOKS","BSE","BSHSL","BSL","BSOFT","BTML","BTTL","BUILDPRO","BUTTERFLY",
"BVCL","BYKE","CALSOFT","CAMLINFINE","CAMPUS","CAMS","CANBK","CANFINHOME","CANHLIFE","CANTABIL",
"CAPACITE","CAPILLARY","CAPITALSFB","CAPLIPOINT","CAPTRUST","CARBORUNIV","CARERATING","CARRARO",
"CARTRADE","CARYSIL","CASTROLIND","CCAVENUE","CCCL","CCHHL","CCL","CDSL","CEATLTD","CEIGALL",
"CEINSYS","CELEBRITY","CELLO","CEMPRO","CENTENKA","CENTEXT","CENTRALBK","CENTRUM","CENTUM",
"CENTURYPLY","CERA","CEREBRAINT","CESC","CEWATER","CGCL","CGPOWER","CHALET","CHAMBLFERT",
"CHEMBOND","CHEMBONDCH","CHEMCON","CHEMFAB","CHEMPLASTS","CHENNPETRO","CHEVIOT","CHOICEIN",
"CHOLAFIN","CHOLAHLDNG","CIEINDIA","CIFL","CINELINE","CINEVISTA","CIPLA","CLEAN","CLEANMAX",
"CLEDUCATE","CLSEL","CMPDI","CMRGREEN","CMSINFO","CNL","COALINDIA","COASTCORP","COCHINSHIP",
"COCKERILL","COFFEEDAY","COFORGE","COHANCE","COLPAL","COMFINTE","COMPINFO","COMPUSOFT","COMSYN",
"CONCOR","CONCORDBIO","CONFIPET","CONSOFINVT","CONTROLPR","CORALFINAC","CORDSCABLE","COROMANDEL",
"CORONA","COSMOFIRST","COUNCODOS","CPCAP","CPEDU","CPPLUS","CRAFTSMAN","CRAMC","CREATIVEYE",
"CREDITACC","CREST","CRISIL","CRIZAC","CROMPTON","CROWN","CSBBANK","CSLFINANCE","CTE","CUB",
"CUBEXTUB","CUMMINSIND","CUPID","CURAA","CYBERMEDIA","CYBERTECH","CYIENT","CYIENTDLM","DABUR",
"DAICHI","DALBHARAT","DALMIASUG","DAMCAPITAL","DAMODARIND","DANGEE","DATAMATICS","DATAPATTNS",
"DAVANGERE","DBCORP","DBEIL","DBL","DBOL","DBREALTY","DBSTOCKBRO","DCAL","DCBBANK","DCI","DCM",
"DCMFINSERV","DCMNVL","DCMSHRIRAM","DCMSIL","DCMSRIND","DCW","DCXINDIA","DDEVPLSTIK","DECCANCE",
"DECNGOLD","DEEDEV","DEEPAKFERT","DEEPAKNTR","DEEPINDS","DELHIVERY","DELPHIFX","DELTACORP",
"DELTAMAGNT","DEN","DENORA","DENTA","DEVIT","DEVX","DEVYANI","DGCONTENT","DHAMPURSUG","DHANBANK",
"DHANUKA","DHARAN","DHARMAJ","DHRUV","DHUNINV","DIACABS","DIAMINESQ","DIAMONDYD","DICIND",
"DIFFNKG","DIGIDRIVE","DIGISPICE","DIGITIDE","DIGJAMLMTD","DISAQ","DISHTV","DIVGIITTS",
"DIVISLAB","DIXON","DJML","DLF","DLINKINDIA","DMART","DMCC","DNAMEDIA","DODLA","DOLATALGO",
"DOLLAR","DOLPHIN","DOMS","DONEAR","DPABHUSHAN","DPSCLTD","DPWIRES","DRAGARWQ","DRCSYSTEMS",
"DREAMFOLKS","DREDGECORP","DRREDDY","DSFCL","DSSL","DTIL","DUCON","DVL","DWARKESH","DYCL",
"DYNAMATECH","DYNPRO","E2E","EASEMYTRIP","EASTSILK","EBGNG","ECLERX","ECOSMOBLTY","EDELWEISS",
"EFCIL","EICHERMOT","EIDPARRY","EIEL","EIFFL","EIHAHOTELS","EIHOTEL","EIMCOELECO","EKC",
"ELANTAS","ELCIDIN","ELDEHSG","ELECON","ELECTCAST","ELECTHERM","ELGIEQUIP","ELGIRUBCO","ELIN",
"ELITECON","ELLEN","ELPROINTL","EMAMILTD","EMAMIPAP","EMAMIREAL","EMBDL","EMCURE","EMIL",
"EMKAY","EMMBI","EMMVEE","EMPOWER","EMSLIMITED","EMUDHRA","ENDURANCE","ENERGYDEV","ENGINERSIN",
"ENIL","ENRIN","ENTERO","EPACK","EPACKPEB","EPIGRAL","EPL","EQUIPPP","EQUITASBNK","ERIS",
"ESABINDIA","ESAFSFB","ESCORTS","ESSARSHPNG","ESSENTIA","ESTER","ETERNAL","ETHOSLTD","EUREKAFORB",
"EUROBOND","EUROPRATIK","EUROTEXIND","EVEREADY","EVERESTIND","EXCELINDUS","EXCELSOFT","EXICOM",
"EXIDEIND","EXPLEOSOL","EXXARO","FABTECH","FACT","FAIRCHEMOR","FAZE3Q","FCL","FCSSOFT","FDC",
"FEDDERSHOL","FEDERALBNK","FEDFINA","FEL","FELDVR","FERMENTA","FIBERWEB","FIEMIND","FILATEX",
"FILATFASH","FINCABLES","FINEORG","FINKURVE","FINOPB","FINPIPE","FIRSTCRY","FISCHER","FIVESTAR",
"FLAIR","FLEXITUFF","FLFL","FLUOROCHEM","FMGOETZE","FMNL","FOCUS","FOODSIN","FORCEMOT","FORTIS",
"FOSECOIND","FRACTAL","FRONTSP","FSL","FUSION","GABRIEL","GAEL","GAIL","GALAPREC","GALAXYSURF",
"GALLANTT","GANDHAR","GANDHITUBE","GANECOS","GANESHBE","GANESHCP","GANESHHOU","GANGAFORGE",
"GANGESSECU","GARFIBRES","GARUDA","GATECH","GATECHDVR","GATEWAY","GAUDIUMIVF","GAYAHWS",
"GAYAPROJ","GCSL","GEECEE","GEEKAYWIRE","GEMAROMA","GENCON","GENESYS","GENUSPAPER","GENUSPOWER",
"GEOJITFSL","GESHIP","GFLLIMITED","GHCL","GHCLTEXTIL","GICHSGFIN","GICL","GICRE","GILLANDERS",
"GILLETTE","GINNIFILA","GIPCL","GKENERGY","GKSL","GKWLIMITED","GLAND","GLAXO","GLENMARK","GLFL",
"GLOBAL","GLOBALE","GLOBALVECT","GLOBE","GLOBECIVIL","GLOBUSSPR","GLOSTERLTD","GLOTTIS","GMBREW",
"GMDCLTD","GMMPFAUDLR","GMRAIRPORT","GMRP&UI","GNA","GNFC","GNRL","GOACARBON","GOCLCORP",
"GOCOLORS","GODAVARIB","GODFRYPHLP","GODIGIT","GODREJAGRO","GODREJCP","GODREJIND","GODREJPROP",
"GOKEX","GOKUL","GOKULAGRO","GOLDENTOBC","GOLDIAM","GOLDTECH","GOODLUCK","GOODYEAR","GOPAL",
"GOYALALUM","GPIL","GPPL","GPTHEALTH","GPTINFRA","GRADIENTE","GRANDOAK","GRANULES","GRAPHITE",
"GRASIM","GRAUWEIL","GRAVISSHO","GRAVITA","GREAVESCOT","GREENLAM","GREENPANEL","GREENPLY",
"GREENPOWER","GRINDWELL","GRINFRA","GRMOVER","GROBTEA","GROWW","GRPLTD","GRSE","GRWRHITECH",
"GSFC","GSLSU","GSPCROP","GSS","GTECJAINX","GTL","GTLINFRA","GTPL","GUFICBIO","GUJALKALI",
"GUJAPOLLO","GUJGASLTD","GUJRAFFIA","GUJTHEM","GULFOILLUB","GULFPETRO","GULPOLY","GVKPIL",
"GVPIL","GVPTECH","GVT&D","HAL","HALDER","HALDYNGL","HALEOSLABS","HAPPSTMNDS","HAPPYFORGE",
"HARDWYN","HARIOMPIPE","HARRMALAYA","HARSHA","HATHWAY","HATSUN","HAVELLS","HAVISHA","HAWKINCOOK",
"HBESD","HBLENGINE","HBSL","HCC","HCG","HCL-INSYS","HCLTECH","HDBFS","HDFCAMC","HDFCBANK",
"HDFCLIFE","HDIL","HEADSUP","HEALTHX","HECPROJECT","HEG","HEIDELBERG","HEMIPROP","HERANBA",
"HERITGFOOD","HEROMOTOCO","HESTERBIO","HEXAGON","HEXATRADEX","HEXT","HFCL","HGINFRA","HGM",
"HGS","HIKAL","HILINFRA","HILTON","HIMATSEIDE","HINDALCO","HINDCOMPOS","HINDCON","HINDCOPPER",
"HINDOILEXP","HINDPETRO","HINDUNILVR","HINDWAREAP","HINDZINC","HIRECT","HISARMETAL","HITECH",
"HITECHCORP","HITECHGEAR","HLEGLAS","HLVLTD","HMAAGRO","HMT","HMVL","HNDFDS","HOMEFIRST",
"HONASA","HONAUT","HONDAPOWER","HPAL","HPIL","HPL","HSCL","HTMEDIA","HUBTOWN","HUDCO",
"HUHTAMAKI","HYBRIDFIN","HYUNDAI","IBULLSLTD","ICDSLTD","ICEMAKE","ICICIAMC","ICICIBANK",
"ICICIGI","ICICIPRULI","ICIL","ICRA","IDBI","IDEA","IDEAFORGE","IDFCFIRSTB","IEX","IFBAGRO",
"IFBIND","IFCI","IFGLEXPOR","IGARASHI","IGCL","IGIL","IGL","IGPL","IIFL","IIFLCAPS","IITL",
"IKIO","IKS","IL&FSENGG","IL&FSTRANS","IMAGICAA","IMFA","IMPAL","INA","INCREDIBLE","INDBANK",
"INDGN","INDHOTEL","INDIACEM","INDIAGLYCO","INDIAMART","INDIANB","INDIANCARD","INDIANHUME",
"INDIASHLTR","INDIGO","INDIGOPNTS","INDIQUBE","INDNIPPON","INDOAMIN","INDOBORAX","INDOCO",
"INDOFARM","INDORAMA","INDOSTAR","INDOTECH","INDOTHAI","INDOUS","INDOWIND","INDPRUD","INDRAMEDCO",
"INDSWFTLAB","INDTERRAIN","INDUSINDBK","INDUSTOWER","INFOBEAN","INFOMEDIA","INFY","INGERRAND",
"INNOVACAP","INNOVANA","INNOVISION","INOXGREEN","INOXINDIA","INOXWIND","INSECTICID","INSPIRISYS",
"INTELLECT","INTENTECH","INTERARCH","INTLCONV","INVENTURE","INVPRECQ","IOB","IOC","IOLCP",
"IONEXCHANG","IPCALAB","IPL","IRB","IRCON","IRCTC","IREDA","IRFC","IRIS","IRISDOREME",
"IRMENERGY","ISFT","ISGEC","ISHANCH","ITC","ITCHOTELS","ITDC","ITI","IVALUE","IVC","IVP","IWP",
"IXIGO","IZMO","J&KBANK","JAGRAN","JAGSNPHARM","JAIBALAJI","JAICORPLTD","JAINREC","JAIPURKURT",
"JAMNAAUTO","JARO","JASH","JAYAGROGN","JAYBARMARU","JAYKAY","JAYNECOIND","JAYSREETEA",
"JBCHEPHARM","JBMA","JETFREIGHT","JGCHEM","JHS","JINDALPHOT","JINDALPOLY","JINDALSAW",
"JINDALSTEL","JINDRILL","JINDWORLD","JIOFIN","JISLDVREQS","JISLJALEQS","JITFINFRA","JKCEMENT",
"JKIL","JKIPL","JKLAKSHMI","JKPAPER","JKTYRE","JLHL","JMA","JMFINANCIL","JNKINDIA","JOCIL",
"JPOLYINVST","JPPOWER","JSFB","JSL","JSLL","JSWCEMENT","JSWDULUX","JSWENERGY","JSWHL","JSWINFRA",
"JSWSTEEL","JTEKTINDIA","JTLIND","JUBLCPL","JUBLFOOD","JUBLINGREA","JUBLPHARMA","JUNIPER",
"JUSTDIAL","JWL","JYOTHYLAB","JYOTICNC","JYOTISTRUC","KABRAEXTRU","KAJARIACER","KAKATCEM",
"KALAMANDIR","KALPATARU","KALYANI","KALYANIFRG","KALYANKJIL","KAMAHOLD","KAMATHOTEL","KAMDHENU",
"KAMOPAINTS","KANANIIND","KANCHI","KANORICHEM","KANPRPLA","KANSAINER","KAPSTON","KARMAENG",
"KARURVYSYA","KAUSHALYA","KAVDEFENCE","KAYA","KAYNES","KCP","KCPSUGIND","KDDL","KEC","KECL",
"KEEPLEARN","KEI","KELLTONTEC","KENNAMET","KERNEX","KESORAMIND","KEYFINSERV","KFINTECH","KHADIM",
"KHAICHEM","KHAITANLTD","KHANDSE","KICL","KILITCH","KIMS","KINGFA","KIOCL","KIRANVYPAR",
"KIRIINDUS","KIRLFER","KIRLOSBROS","KIRLOSENG","KIRLOSIND","KIRLPNU","KISSHT","KITEX","KKCL",
"KLBRENG-B","KMEW","KMSUGAR","KNAGRI","KNRCON","KOHINOOR","KOKUYOCMLN","KOLTEPATIL","KOPRAN",
"KOTAKBANK","KOTARISUG","KOTHARIPET","KOTHARIPRO","KOTIC","KOTYARK","KOVAI","KPEL","KPIGREEN",
"KPIL","KPITTECH","KPL","KPRMILL","KRBL","KREBSBIO","KRIDHANINF","KRISHANA","KRISHIVAL",
"KRISHNADEF","KRITI","KRITIKA","KRITINUT","KRN","KRONOX","KROSS","KRSNAA","KRYSTAL","KSB",
"KSCL","KSHINTL","KSHITIJPOL","KSL","KSOLVES","KSR","KTKBANK","KUANTUM","KWIL","LAGNAM",
"LAHOTIOV","LAKPRE","LAL","LALPATHLAB","LAMBODHARA","LANCORHOL","LANDMARK","LANDSMILL","LAOPALA",
"LASA","LATENTVIEW","LATTEYS","LAURUSLABS","LAXMICOT","LAXMIDENTL","LAXMIINDIA","LCCINFOTEC",
"LEMERITE","LEMONTREE","LENSKART","LEXUS","LFIC","LGBBROSLTD","LGEINDIA","LGHL","LIBAS",
"LIBERTSHOE","LICHSGFIN","LICI","LIKHITHA","LINC","LINCOLN","LINDEINDIA","LLOYDSENGG","LLOYDSENT",
"LLOYDSME","LMW","LODHA","LOKESHMACH","LORDSCHLO","LOTUSDEV","LOTUSEYE","LOVABLE","LOYALTEX",
"LPDC","LT","LTF","LTFOODS","LTM","LTTS","LUMAXIND","LUMAXTECH","LUPIN","LUXIND","LXCHEM",
"LYKALABS","LYPSAGEMS","M&M","M&MFIN","MAANALU","MACPOWER","MADHAV","MADHAVIPL","MADHUCON",
"MADRASFERT","MAFATIND","MAGADSUGAR","MAGNUM","MAHABANK","MAHAPEXLTD","MAHASTEEL","MAHEPC",
"MAHESHWARI","MAHLIFE","MAHLOG","MAHSCOOTER","MAHSEAMLES","MAITHANALL","MAJESAUT","MALLCOM",
"MALUPAPER","MAMATA","MANAKALUCO","MANAKCOAT","MANAKSIA","MANAKSTEEL","MANALIPETC","MANAPPURAM",
"MANBA","MANCREDIT","MANGALAM","MANGLMCEM","MANINDS","MANINFRA","MANKIND","MANOMAY","MANORAMA",
"MANORG","MANUGRAPH","MANYAVAR","MAPMYINDIA","MARALOVER","MARATHON","MARICO","MARINE",
"MARKOLINES","MARKSANS","MARSONS","MARUTI","MASFIN","MASKINVEST","MASTEK","MASTERTR","MATRIMONY",
"MAWANASUG","MAXESTATES","MAXHEALTH","MAXIND","MAYURUNIQ","MAZDA","MAZDOCK","MBAPL","MBEL",
"MBLINFRA","MCCHRLS-B","MCL","MCLEODRUSS","MCLOUD","MCX","MEDANTA","MEDIASSIST","MEDICAMEQ",
"MEDICO","MEDPLUS","MEESHO","MEGASTAR","MEIL","MENNPIS","MENONBE","MEP","MERCANTILE","MERCURYEV",
"METROBRAND","METROGLOBL","METROPOLIS","MFML","MFSL","MGEL","MGL","MHLXMIRU","MHRIL","MICEL",
"MIDHANI","MIDWESTLTD","MINDACORP","MINDTECK","MIRCELECTR","MIRZAINT","MITCON","MITTAL","MKPL",
"MMFL","MMP","MMTC","MMWL","MOBIKWIK","MODINATUR","MODIRUBBER","MODIS","MODISONLTD","MODTHREAD",
"MOHITIND","MOIL","MOKSH","MOL","MOLDTECH","MOLDTKPAC","MONARCH","MONEYBOXX","MONTECARLO",
"MORARJEE","MOREPENLAB","MOSCHIP","MOTHERSON","MOTILALOFS","MOTISONS","MOTOGENFIN","MPHASIS",
"MPSLTD","MRF","MRPL","MSPL","MSTCLTD","MSUMI","MTARTECH","MTEDUCARE","MTNL","MUFIN","MUFTI",
"MUKANDLTD","MUKKA","MUKTAARTS","MUNJALAU","MUNJALSHOW","MURUDCERA","MUTHOOTCAP","MUTHOOTFIN",
"MUTHOOTMF","MVGJL","MWL","NACLIND","NAGREEKCAP","NAGREEKEXP","NAHARCAP","NAHARINDUS","NAHARPOLY",
"NAHARSPING","NAM-INDIA","NARMADA","NATCAPSUQ","NATCOPHARM","NATHBIOGEN","NATIONALUM","NATIONSTD",
"NAUKRI","NAVA","NAVINFLUOR","NAVKARCORP","NAVKARURB","NAVNETEDUL","NAZARA","NBCC","NBIFIN","NCC",
"NCLIND","NDGL","NDL","NDLVENTURE","NDRAUTO","NDTV","NEAGI","NECCLTD","NECLIFE","NELCAST","NELCO",
"NEOGEN","NEPHROPLUS","NESCO","NESTLEIND","NETWEB","NETWORK18","NEULANDLAB","NEWGEN","NEXTMEDIA",
"NFL","NGIL","NGLFINE","NH","NHPC","NIACL","NIBE","NIBL","NIITLTD","NIITMTS","NILAINFRA",
"NILASPACES","NILE","NILKAMAL","NIMBSPROJ","NINSYS","NIPPOBATRY","NIRAJ","NIRAJISPAT","NIRLON",
"NITCO","NITINSPIN","NITIRAJ","NITTAGELA","NIVABUPA","NKIND","NLCINDIA","NMDC","NOCIL","NOIDATOLL",
"NORBTEAEXP","NORTHARC","NOVAAGRI","NOVARTIND","NPST","NRAIL","NRBBEARING","NRL","NSIL","NSLNISP",
"NTPC","NTPCGREEN","NUCLEUS","NURECA","NUVAMA","NUVOCO","NYKAA","OAL","OBCL","OBEROIRLTY",
"OCCLLTD","ODIGMA","OFSS","OIL","OILCOUNTUB","OLAELEC","OLECTRA","OMAXAUTO","OMAXE","OMFREIGHT",
"OMINFRAL","OMNI","OMPOWER","ONELIFECAP","ONEPOINT","ONESOURCE","ONGC","ONMOBILE","ONWARDTEC",
"OPTIEMUS","ORBTEXP","ORCHASP","ORCHPHARMA","ORICONENT","ORIENTALTL","ORIENTBELL","ORIENTCEM",
"ORIENTCER","ORIENTELEC","ORIENTHOT","ORIENTLTD","ORIENTPPR","ORIENTTECH","ORISSAMINE","ORKLAINDIA",
"ORTEL","ORTINGLOBE","OSIAHYPER","OSWALAGRO","OSWALGREEN","OSWALPUMPS","OSWALSEEDS","PACEDIGITK",
"PAGEIND","PAISALO","PAKKA","PALASHSECU","PALREDTEC","PANACEABIO","PANACHE","PANAMAPET","PANSARI",
"PAR","PARACABLES","PARADEEP","PARAGMILK","PARAS","PARASPETRO","PARKHOSPS","PARKHOTELS","PARSVNATH",
"PASHUPATI","PASUPTAC","PATANJALI","PATELENG","PATELRMART","PATINTLOG","PAUSHAKLTD","PAVNAIND",
"PAYTM","PCBL","PCJEWELLER","PDMJEPAPER","PDSL","PEARLPOLY","PENIND","PENINLAND","PERSISTENT",
"PETRONET","PFC","PFIZER","PFOCUS","PFS","PGEL","PGHH","PGHL","PGIL","PHOENIXLTD","PICCADIL",
"PIDILITIND","PIGL","PIIND","PILANIINVS","PILITA","PINELABS","PIONEEREMB","PIONRINV","PIRAMALFIN",
"PITTIENG","PIXTRANS","PKTEA","PLASTIBLEN","PLATIND","PLAZACABLE","PML","PNB","PNBGILTS",
"PNBHOUSING","PNC","PNCINFRA","PNGJL","PNGSREVA","POCL","PODDARMENT","POKARNA","POLICYBZR",
"POLYCAB","POLYMED","POLYPLEX","PONNIERODE","POONAWALLA","POWERGRID","POWERICA","POWERINDIA",
"POWERMECH","PPAP","PPL","PPLPHARMA","PRABHA","PRADPME","PRAENG","PRAJIND","PRAKASH","PRAKASHSTL",
"PRAVEG","PRAXIS","PRECAM","PRECOT","PRECWIRE","PREMCO","PREMEXPLN","PREMIER","PREMIERENE",
"PREMIERPOL","PRESTIGE","PRICOLLTD","PRIMESECU","PRIMO","PRINCEPIPE","PRITI","PRITIKAUTO",
"PRIVISCL","PROSTARM","PROTEAN","PROZONER","PRSMJOHNSN","PRUDENT","PRUDMOULI","PSB","PSPPROJECT",
"PTC","PTCIL","PTL","PUNJABCHEM","PURVA","PVP","PVRINOX","PVSL","PWL","PYRAMID","QMSMEDI",
"QPOWER","QUADFUTURE","QUESS","QUICKHEAL","QUINT","RACE","RACLGEAR","RADAAN","RADHIKAJWE",
"RADIANTCMS","RADICO","RADIOCITY","RAILTEL","RAIN","RAINBOW","RAJESHEXPO","RAJMET","RAJOOENG",
"RAJPALAYAM","RAJRATAN","RAJRILTD","RAJSREESUG","RAJTV","RALLIS","RAMANEWS","RAMAPHO","RAMASTEEL",
"RAMCOCEM","RAMCOIND","RAMCOSYS","RAMKY","RAMRAT","RANASUG","RANEHOLDIN","RATEGAIN","RATNAMANI",
"RATNAVEER","RAYMOND","RAYMONDLSL","RAYMONDREL","RBA","RBLBANK","RBZJEWEL","RCF","RCOM","RECLTD",
"REDINGTON","REDTAPE","REFEX","REGAAL","REGENCERAM","RELAXO","RELCHEMQ","RELIABLE","RELIANCE",
"RELIGARE","RELTD","RELTD-RE","REMSONSIND","RENUKA","REPCOHOME","REPL","REPRO","RESPONIND",
"RETAIL","RGL","RHETAN","RHFL","RHIM","RHL","RICOAUTO","RIIL","RISHABH","RITCO","RITES","RKDL",
"RKEC","RKFORGE","RKSWAMY","RMC","RMDRIP","RML","RNBDENIMS","ROHLTD","ROLEXRINGS","ROLLT","ROML",
"ROSSARI","ROSSELLIND","ROSSTECH","ROTO","ROUTE","RPEL","RPGLIFE","RPOWER","RPPINFRA","RPPL",
"RPSGVENT","RPTECH","RRIL","RRKABEL","RSDFIN","RSL","RSSOFTWARE","RSWM","RSYSTEMS","RTNINDIA",
"RTNPOWER","RUBFILA","RUBICON","RUBYMILLS","RUCHINFRA","RUCHIRA","RUDRA","RUPA","RUSHIL",
"RUSTOMJEE","RVHL","RVNL","RVTH","S&SPOWER","SAATVIKGL","SABEVENTS","SADBHAV","SADBHIN",
"SADHNANIQ","SAFARI","SAGARDEEP","SAGCEM","SAGILITY","SAHLIBHFI","SAHYADRI","SAIL","SAILIFE",
"SAIPARENT","SAKAR","SAKHTISUG","SAKSOFT","SAKUMA","SALASAR","SALONA","SALSTEEL","SALZERELEC",
"SAMBHAAV","SAMBHV","SAMHI","SAMMAANCAP","SAMPANN","SANATHAN","SANDESH","SANDHAR","SANDUMA",
"SANGAMIND","SANGHVIMOV","SANGINITA","SANOFI","SANOFICONR","SANSERA","SANSTAR","SANWARIA",
"SAPPHIRE","SAPPL","SARDAEN","SAREGAMA","SARLAPOLY","SARVESHWAR","SASKEN","SATIA","SATIN",
"SAURASHCEM","SAYAJIHOTL","SBC","SBCL","SBFC","SBGLP","SBICARD","SBILIFE","SBIN","SCANSTL",
"SCHAEFFLER","SCHAND","SCHNEIDER","SCI","SCILAL","SCODATUBES","SCPL","SDBL","SEAMECLTD","SECMARK",
"SECURKLOUD","SEDEMAC","SEIL","SEJALLTD","SELMC","SEMAC","SENCO","SENORES","SEPC","SERVOTECH",
"SESHAPAPER","SETCO","SETL","SETUINFRA","SEYAIND","SFL","SGFIN","SGIL","SGL","SGMART","SHADOWFAX",
"SHAH","SHAH-RE1","SHAHALLOYS","SHAILY","SHAKTIPUMP","SHALBY","SHALPAINTS","SHANKARA","SHANTI",
"SHANTIGEAR","SHANTIGOLD","SHARDACROP","SHARDAMOTR","SHARDUL","SHAREINDIA","SHBAJRG","SHEKHAWATI",
"SHEMAROO","SHILCTECH","SHILPAMED","SHINDL","SHIVALIK","SHIVAMAUTO","SHIVAMILLS","SHIVATEX",
"SHIVAUM","SHK","SHOPERSTOP","SHRADHA","SHREDIGCEM","SHREECEM","SHREEJISPG","SHREEPUSHK",
"SHREERAMA","SHRENIK","SHREYANIND","SHRIKRISH","SHRINGARMS","SHRIPISTON","SHRIRAMFIN","SHRIRAMPPS",
"SHYAMCENT","SHYAMMETL","SHYAMTEL","SICAGEN","SICALLOG","SIEMENS","SIGACHI","SIGIND","SIGMA",
"SIGMAADV","SIGNATURE","SIGNPOST","SIKA","SIKKO","SIL","SILGO","SILINV","SILLYMONKS","SILVERTUC",
"SIMBHALS","SIMPLEXINF","SINCLAIR","SINDHUTRAD","SINGERIND","SINTERCOM","SIRCA","SIS","SITINET",
"SIYSIL","SJS","SJVN","SKFINDIA","SKFINDUS","SKIPPER","SKMEGGPROD","SKYGOLD","SMARTLINK",
"SMARTWORKS","SMCGLOBAL","SMLMAH","SMLT","SMSPHARMA","SNOWMAN","SOBHA","SOFTTECH","SOLARA",
"SOLARINDS","SOLARWORLD","SOLEX","SOMANYCERA","SOMATEX","SOMICONVEY","SONACOMS","SONAL","SONAMLTD",
"SONATSOFTW","SOTL","SOUTHBANK","SOUTHWEST","SPAL","SPANDANA","SPARC","SPCENET","SPECIALITY",
"SPECTRUM","SPENCERS","SPIC","SPLIL","SPLPETRO","SPMLINFRA","SPORTKING","SRD","SREEL","SRF",
"SRGHFL","SRHHYPOLTD","SRM","SRTL","SSDL","SSWL","STALLION","STANLEY","STAR","STARCEMENT",
"STARHEALTH","STARPAPER","STARTECK","STCINDIA","STEELCAS","STEELCITY","STEELXIND","STEL",
"STERTOOLS","STLNETWORK","STLTECH","STOVEKRAFT","STUDDS","STYL","STYLAMIND","STYLEBAAZA",
"STYRENIX","SUBEXLTD","SUBROS","SUDARCOLOR","SUDARSCHEM","SUDEEPPHRM","SUKHJITS","SULA",
"SUMEETINDS","SUMICHEM","SUMIT","SUMMITSEC","SUNCLAY","SUNDARAM","SUNDARMFIN","SUNDRMBRAK",
"SUNDRMFAST","SUNDROP","SUNFLAG","SUNPHARMA","SUNTECK","SUNTV","SUPERHOUSE","SUPERSPIN","SUPRAJIT",
"SUPREME","SUPREMEENG","SUPREMEIND","SUPREMEINF","SUPRIYA","SURAJEST","SURAJLTD","SURAKSHA",
"SURANASOL","SURANAT&P","SURYALA","SURYALAXMI","SURYAROSNI","SURYODAY","SUTLEJTEX","SUVEN",
"SUVIDHAA","SUYOG","SUZLON","SVLL","SVPGLOB","SWANCORP","SWANDEF","SWARAJENG","SWELECTES",
"SWIGGY","SWSOLAR","SYMPHONY","SYNCOMF","SYNGENE","SYRMA","SYSTMTXC","TAALTECH","TAINWALCHM",
"TAJGVK","TAKE","TALBROAUTO","TAMBOLIIN","TANLA","TARACHAND","TARAPUR","TARC","TARIL","TARMAT",
"TARSONS","TASTYBITE","TATACAP","TATACHEM","TATACOMM","TATACONSUM","TATAELXSI","TATAINVEST",
"TATAPOWER","TATASTEEL","TATATECH","TATVA","TBOTEK","TBZ","TCC","TCI","TCIEXP","TCIFINANCE",
"TCPLPACK","TCS","TDPOWERSYS","TEAMGTY","TEAMLEASE","TECHM","TECHNOE","TECHNVISN","TECILCHEM",
"TEGA","TEJASNET","TEMBO","TENNIND","TERASOFT","TEXINFRA","TEXMOPIPES","TEXRAIL","TFCILTD","TFL",
"TGBHOTELS","THACKER","THAKDEV","THANGAMAYL","THEINVEST","THEJO","THELEELA","THEMISMED","THERMAX",
"THOMASCOOK","THOMASCOTT","THYROCARE","TI","TICL","TIGERLOGS","TIIL","TIINDIA","TIJARIA","TIL",
"TIMETECHNO","TIMEX","TIMKEN","TINNARUBR","TIPSFILMS","TIPSMUSIC","TIRUMALCHM","TIRUPATIFL",
"TITAGARH","TITAN","TMB","TMCV","TMPV","TNPETRO","TNPL","TNTELE","TOKYOPLAST","TOLINS",
"TORNTPHARM","TORNTPOWER","TOTAL","TOUCHWOOD","TPHQ","TPLPLASTEH","TRACXN","TRANSPEK","TRANSRAILL",
"TRANSWORLD","TRAVELFOOD","TREEHOUSE","TREJHARA","TREL","TRENT","TRF","TRIDENT","TRIGYN",
"TRITURBINE","TRIVENI","TRU","TRUALT","TSFINV","TTKHLTCARE","TTKPRESTIG","TTL","TTML","TVSELECT",
"TVSHLTD","TVSMOTOR","TVSSCS","TVSSRICHAK","TVTODAY","TVVISION","UBL","UCAL","UCOBANK","UDS",
"UEL","UFBL","UFLEX","UFO","UGARSUGAR","UGROCAP","UJJIVANSFB","ULTRACEMCO","ULTRAMAR","UMAEXPORTS",
"UMESLTD","UMIYA-MRO","UNICHEMLAB","UNIDT","UNIECOM","UNIENTER","UNIINFO","UNIMECH","UNIONBANK",
"UNIPARTS","UNITDSPR","UNITECH","UNITEDPOLY","UNITEDTEA","UNIVASTU","UNIVCABLES","UNIVPHOTO",
"UNOMINDA","UPL","URAVIDEF","URBANCO","URJA","USHAMART","USK","UTIAMC","UTKARSHBNK","UTLSOLAR",
"UTTAMSUGAR","UYFINCORP","V2RETAIL","VADILALIND","VAIBHAVGBL","VAISHALI","VAKRANGEE","VALIANTLAB",
"VALIANTORG","VAML","VARDHACRLC","VARDMNPOLY","VARROC","VASCONEQ","VASWANI","VBL","VCL","VEDL",
"VEDPOWER","VEEDOL","VELJAN","VENKEYS","VENTIVE","VENUSPIPES","VENUSREM","VERANDA","VERTOZ",
"VESUVIUS","VETO","VGL","VGUARD","VHL","VHLTD","VIDHIING","VIDYAWIRES","VIJAYA","VIJIFIN",
"VIKASECO","VIKASLIFE","VIKRAMSOLR","VIKRAN","VIMTALABS","VINATIORGA","VINCOFE","VINDHYATEL",
"VINEETLAB","VINNY","VINYLINDIA","VIPCLOTHNG","VIPIND","VIPULLTD","VIRINCHI","VISACHROME",
"VISAKAIND","VISHNU","VISHWARAJ","VISL","VITAL","VIVIANA","VIVIDHA","VIVIMEDLAB","VIYASH",
"VLEGOV","VLSFINANCE","VMART","VMM","VMSTMT","VOGL","VOLTAMP","VOLTAS","VPRPL","VRAJ","VRLLOG",
"VSSL","VSTIND","VSTL","VSTTILLERS","VTL","WAAREEENER","WAAREEINDO","WAAREERTL","WABAG","WAKEFIT",
"WALCHANNAG","WANBURY","WCIL","WEALTH","WEBELSOLAR","WEIZMANIND","WEL","WELCORP","WELENT","WELINV",
"WELSPLSOL","WELSPUNLIV","WENDT","WESTLIFE","WEWIN","WEWORK","WHEELS","WHIRLPOOL","WILLAMAGOR",
"WINDLAS","WINDMACHIN","WINSOME","WIPL","WIPRO","WOCKPHARMA","WONDERLA","WORTHPERI","WPIL","WSI",
"WSTCSTPAPR","XCHANGING","XELPMOC","XPROINDIA","XTGLOBAL","YASHO","YATHARTH","YATRA","YESBANK",
"YUKEN","ZAGGLE","ZEEL","ZEELEARN","ZEEMEDIA","ZENITHEXPO","ZENITHSTL","ZENSARTECH","ZENTEC",
"ZFCVINDIA","ZFSTEERING","ZIMLAB","ZODIAC","ZODIACLOTH","ZOTA","ZSARACOM","ZUARI","ZUARIIND",
"ZYDUSLIFE","ZYDUSWELL",
]

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_TO       = os.environ.get("EMAIL_TO", "")
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")

POLL_INTERVAL  = 15          # seconds
SEEN_FILE      = "seen_announcements.json"
MAX_SEEN       = 5000
GROQ_MODEL     = "llama-3.3-70b-versatile"
WATCHLIST_SET  = set(s.upper() for s in WATCHLIST)

# ============================================================
# GROQ CLIENT
# ============================================================

GROQ_CLIENT = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ============================================================
# NSE SESSION
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer":    "https://www.nseindia.com/",
    "Accept":     "application/json, text/plain, */*",
}

session = requests.Session()
session.headers.update(HEADERS)

def now():
    return datetime.now().strftime("%H:%M:%S")

def log(msg):
    print(f"[{now()}] {msg}", flush=True)

# ============================================================
# HEALTH SERVER
# ============================================================

def start_healthcheck_server():
    port = int(os.environ.get("PORT", 8080))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args):
            pass

    server = HTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log(f"Healthcheck server listening on :{port}")

# ============================================================
# NSE HELPERS
# ============================================================

def refresh_nse_cookies():
    try:
        session.get("https://www.nseindia.com", timeout=10)
        log("NSE cookies refreshed.")
    except Exception as e:
        log(f"Cookie refresh error: {e}")

def fetch_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code in (401, 403):
            log(f"NSE {resp.status_code} — refreshing cookies and retrying.")
            refresh_nse_cookies()
            resp = session.get(url, timeout=10)
        if resp.status_code != 200:
            log(f"NSE unexpected status {resp.status_code}")
            return []
        return resp.json()
    except Exception as e:
        log(f"Fetch error: {e}")
        return []

# ============================================================
# STORAGE
# ============================================================

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            log(f"Failed to load seen file, starting fresh: {e}")
    return set()

def save_seen(seen):
    try:
        trimmed = seen
        if len(trimmed) > MAX_SEEN:
            trimmed = set(list(trimmed)[-MAX_SEEN:])
        with open(SEEN_FILE, "w") as f:
            json.dump(list(trimmed), f)
        return trimmed
    except Exception as e:
        log(f"Failed to save seen file: {e}")
        return seen

# ============================================================
# PDF TEXT
# ============================================================

def download_pdf_text(pdf_url):
    try:
        if not pdf_url.startswith("http"):
            pdf_url = f"https://nsearchives.nseindia.com/{pdf_url}"
        resp = session.get(pdf_url, timeout=20)
        reader = PdfReader(io.BytesIO(resp.content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) > 10000:
                break
        return text[:10000]
    except Exception as e:
        log(f"PDF download error: {e}")
        return ""

# ============================================================
# AI SUMMARY (GROQ)
# ============================================================

def summarize_with_groq(pdf_text, subject=""):
    if not GROQ_CLIENT:
        return "(No GROQ_API_KEY set — skipping summary)"

    # If no PDF text, try to summarise just the subject line
    content = pdf_text if pdf_text else f"Announcement subject: {subject}"
    if not content.strip():
        return "(Nothing to summarise)"

    prompt = (
        "You are a financial analyst assistant. "
        "Read the following NSE corporate announcement and give a concise summary "
        "in 2-3 bullet points. Each bullet must be under 20 words. "
        "Preserve all numbers exactly as they appear.\n\n"
        + content
    )

    try:
        chat = GROQ_CLIENT.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        log(f"Groq error: {e}")
        return "(AI summary failed)"

# ============================================================
# EMAIL — rich HTML
# ============================================================

def build_html(item, summary, pdf_url):
    symbol  = item.get("symbol", "N/A")
    subject = item.get("subject", "N/A")
    seq     = item.get("an_seq_num", "")
    cat     = item.get("desc", item.get("category", ""))
    ts      = item.get("exchdisstime", item.get("sort_date", ""))

    # format summary bullets into styled list
    lines = [l.strip() for l in summary.splitlines() if l.strip()]
    bullets_html = "".join(
        f'<li style="margin-bottom:6px;">{l.lstrip("-•* ")}</li>'
        for l in lines
    )

    pdf_link = (
        f'<a href="{pdf_url}" style="display:inline-block;margin-top:12px;'
        f'padding:8px 18px;background:#1a56db;color:#fff;border-radius:5px;'
        f'text-decoration:none;font-size:14px;">📄 Open Filing PDF</a>'
        if pdf_url else ""
    )

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#f4f6f9;padding:24px;margin:0;">
  <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;
              box-shadow:0 2px 8px rgba(0,0,0,.1);overflow:hidden;">

    <!-- Header -->
    <div style="background:#1a56db;padding:20px 24px;">
      <h1 style="margin:0;color:#fff;font-size:22px;">📢 NSE Alert: {symbol}</h1>
      <p style="margin:4px 0 0;color:#c7d9ff;font-size:13px;">{ts}</p>
    </div>

    <!-- Body -->
    <div style="padding:24px;">

      <table style="width:100%;border-collapse:collapse;margin-bottom:18px;font-size:14px;">
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;width:130px;
                     border:1px solid #dde3f0;">Symbol</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;font-weight:bold;
                     color:#1a56db;">{symbol}</td>
        </tr>
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;
                     border:1px solid #dde3f0;">Category</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;">{cat}</td>
        </tr>
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;
                     border:1px solid #dde3f0;">Subject</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;">{subject}</td>
        </tr>
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;
                     border:1px solid #dde3f0;">Seq #</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;color:#888;">{seq}</td>
        </tr>
      </table>

      <h3 style="margin:0 0 10px;font-size:15px;color:#333;">🤖 AI Summary</h3>
      <ul style="background:#f8f9fc;border-left:4px solid #1a56db;padding:14px 14px 14px 30px;
                 margin:0;border-radius:0 6px 6px 0;font-size:14px;color:#333;line-height:1.6;">
        {bullets_html}
      </ul>

      {pdf_link}

    </div>

    <!-- Footer -->
    <div style="background:#f0f4ff;padding:12px 24px;font-size:12px;color:#888;text-align:center;">
      NSE Announcement Watcher • Auto-generated alert
    </div>

  </div>
</body>
</html>
"""

def send_email(item, summary):
    if not RESEND_API_KEY or not EMAIL_TO:
        log("Email config missing — skipping.")
        return

    symbol  = item.get("symbol", "UNKNOWN")
    subject = item.get("subject", "")
    pdf     = item.get("attchmntFile", "")
    if pdf and not pdf.startswith("http"):
        pdf = f"https://nsearchives.nseindia.com/{pdf}"

    html = build_html(item, summary, pdf)
    email_subject = f"NSE 📢 {symbol}: {subject[:60]}{'…' if len(subject) > 60 else ''}"

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    "onboarding@resend.dev",
                "to":      [EMAIL_TO],
                "subject": email_subject,
                "html":    html,
            },
            timeout=10,
        )
        if resp.status_code >= 300:
            log(f"Email FAILED ({resp.status_code}): {resp.text[:200]}")
        else:
            log(f"✅ Email sent → {symbol}: {subject[:60]}")
    except Exception as e:
        log(f"Email error: {e}")

# ============================================================
# STARTUP TEST EMAIL
# ============================================================

def send_test_email():
    if not RESEND_API_KEY or not EMAIL_TO:
        log("Skipping startup test email — RESEND_API_KEY or EMAIL_TO not set.")
        return
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    "onboarding@resend.dev",
                "to":      [EMAIL_TO],
                "subject": "NSE Watcher started ✅",
                "html":    "<p>Watcher is running. You will receive alerts for watchlist matches.</p>",
            },
            timeout=10,
        )
        if resp.status_code >= 300:
            log(f"Startup test email FAILED ({resp.status_code}): {resp.text[:300]}")
        else:
            log("Startup test email sent ✅")
    except Exception as e:
        log(f"Startup test email error: {e}")

# ============================================================
# FORCE-SEND TEST — grabs the very first announcement from NSE
# and sends a real alert email so you can verify the full flow
# Set env var FORCE_TEST_EMAIL=1 to trigger on startup
# ============================================================

def force_test_announcement_email():
    log("FORCE_TEST_EMAIL=1 detected — fetching live announcement to test full email flow...")
    data = fetch_announcements()
    if not data:
        log("No announcements returned from NSE for force-test.")
        return

    # pick the first announcement that has a PDF, otherwise just use first
    item = next((x for x in data if x.get("attchmntFile")), data[0])
    symbol  = item.get("symbol", "TEST")
    subject = item.get("subject", "")
    pdf     = item.get("attchmntFile", "")

    log(f"Force-test using: {symbol} | {subject[:60]}")

    text    = download_pdf_text(pdf) if pdf else ""
    summary = summarize_with_groq(text, subject)

    log(f"AI Summary:\n{summary}")
    send_email(item, summary)

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    start_healthcheck_server()
    refresh_nse_cookies()
    send_test_email()

    # Optional: force a real announcement email at startup to verify pipeline
    if os.environ.get("FORCE_TEST_EMAIL", "").strip() == "1":
        force_test_announcement_email()

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen announcement IDs.")

    poll_count = 0

    while True:
        try:
            poll_count += 1
            data = fetch_announcements()
            log(f"Poll #{poll_count}: {len(data)} announcements from NSE.")

            # Log first 3 raw items each poll for visibility
            for item in data[:3]:
                log(
                    f"  → {item.get('symbol','?')} | seq={item.get('an_seq_num','?')} "
                    f"| {item.get('subject','')[:50]}"
                )

            new_count = 0
            for item in data:
                seq = (
                    item.get("an_seq_num")
                    or item.get("symbol", "") + "|" + item.get("attchmntFile", "")
                )
                
                if seq in seen:
                    continue
                
                seen.add(seq)
                new_count += 1

                symbol = item.get("symbol", "").upper()

                if symbol in WATCHLIST_SET:
                    log(f"MATCH FOUND: {symbol}")
                    log(f"NEW: {symbol}")

                pdf     = item.get("attchmntFile", "")
                text    = download_pdf_text(pdf) if pdf else ""
                summary = summarize_with_groq(text, item.get("subject", ""))

                log(f"   Summary: {summary[:120]}")
                send_email(item, summary)

            if new_count:
                log(f"  {new_count} new announcement(s) processed this poll.")

            seen = save_seen(seen)

        except Exception:
            log("Unhandled error in main loop:")
            traceback.print_exc()

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
