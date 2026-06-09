#Testing Package

from lingua import Language, LanguageDetectorBuilder


languages = [Language.ENGLISH, Language.IRISH] #Language needs a capital - I cba
builder = LanguageDetectorBuilder.from_languages(*languages)
builder = builder.with_minimum_relative_distance(0.95)
detector = builder.build()


text = """Aontaím le go leor rudaí is a bhí an Teachta Toole ag rá, go háirithe maidir le daoine faoi mhíchumas. Tá sé an-tábhachtach go mbíonn muid ag smaoineamh faoi na daoine sin. The Minister of State is aware of the work of Ciarán Delaney in Cork. In Dublin, bíonn go leor daoine faoi mhíchumas ag cur glaoch ar m’oifig. Is é an rud is uafásaí ná a bheith ag éisteacht leis na scéalta sin, go háirithe nuair a mhíníonn siad go raibh siad ag iarraidh dul chun na hoibre an lá sin, but the bus came and there was already someone on it with a pram. As a result, I could not get on. They are working. There are times people should move or when there is already one person on board. I welcome the announcement that there will be two or three spots for people with disabilities. As my colleague mentioned, it is very important.

I welcome the opportunity to speak on this Bill. Before I begin criticising the NTA, I want to compliment a member of Dublin Bus. I recently submitted a query. I had response back within 12 hours that I was able to give it to a very happy constituent. I compliment the CEO of Dublin Bus for that response and for coming out to the area behind Clontarf bus depot. It has been the site of absolute destruction for the past number of years. There was an issue as to whether Dublin City Council or Bus Éireann owned the land. It is now confirmed Dublin City Council owns it, so I look forward to getting the area dealt with.

On the Bill, BusConnects has been changing a lot of parts of this city and other cities. I support the extension of the NTA but there are limitations to how much I support it in the sense of how many imperfections there are currently. We need to deliver for those people.

To go back to what I said at the start, it is not acceptable that we do not have a transport system that is fully accessible. A lot of great work has been done but to give people with disabilities complete support, we have to have a public transport system they can trust. I was in Switzerland recently and I saw how accessible public transport can and should be. On the broader issue of accessibility, if the Bill is going to mean anything, it has to not only be for people who are able bodied but also for people who cannot access every single aspect of our society that is private. We should provide them with a public service they can access; a public transport system for everyone.

Another issue I find with the NTA, which has been mentioned by multiple Deputies, is the Leap card system. I know money has been invested in the current plan, but I urge the Minister of State to re-examine it. I am a mechanical engineer, not an electronic engineer, but I have asked my friends if a system could be used for the phone to mimic the ETF from the Leap card. Such a system would be much quicker. The officials from the Department are looking at me. They probably have a good answer in respect of that matter. I tabled a few parliamentary questions in respect of it.

I asked if the National Transport Authority determined that the existing Leap card validator and ticketing infrastructure could not support direct contactless payment by bank card or mobile phone simulations, if any technical or operational assessment had been carried out in this regard, and if the Minister would make a statement on the matter. I received a response but it did not really address the question that I asked, so I have submitted another one.

What is most frustrating for members of the public - it happens to me when I am going to get the bus home - is that none of us has cash anymore. If you do not have one, or if you forget your Leap card, you have to go and get cash out. I do not carry a wallet. Where are you going to go? You are nearly forced to go into the put to get cash back. It is not good for the Irish people. We need to look into this, especially because of where the 130 stop is.

We need to look at making it accessible not only for those with disabilities but also for everyone to encourage them to use public transport. People are like water. They go the fastest route. If you are on the way home, and you see that you can get on the bus, use your phone, tap it and get on, why would you not do it? It would be a lot simpler.

The Leap card system needs to be examined. When I was starting school, it was revolutionary, that is, you did not have to have 65 cent for the bus. The fare has gone up a good bit since then. What is the timeline for the full contactless integration across the network and what is the plan to ensure that every bus stop and every route will enable contactless payment because if we are to extend this NTA framework to Cork, Galway, Limerick, Waterford, Meath, Westmeath and all those places outside the M50 the free travel scheme is another area that we need to examine? People are constantly asking me this on the doorstep so I would like if the Department could issue a statement on it. I understand that there has been money invested in another alternative but I would ask that we stop and re-examine alternatives that other countries have done. The Minister of State will be aware I always want to be constructive and to offer solutions so I would like that to be examined.

I want to highlight the BusConnects issues that have been brought to my attention by residents in Marino whose bus route was recently changed, particularly by the elderly, children and young adults with disabilities who have a set routine. They have learnt that set routine and without any consultation with them, their bus route terminal changed. If a person has learned that set routine of getting into town every day and does not like changes in their routine, that specific small change could really affect that person. Also, the elderly people are now going down an unfamiliar route. Anyone is vulnerable and is not used to the end and I would like that to be examined. I understand there are huge changes on St. Stephen's Green and the NTA will have to reroute some of these routes, but I would like it to be examined.

Another issue I would like to highlight is the recent maritime festival in Howth in north Dublin. We knew there would be thousands of people there. Every year there are thousands of people there but it was like people were going for a meet and greet in the DART - going to see Santa outside. There were four lines of people waiting to get the only DART out of Binn Éadair. If we have a causation and clear data that people will be in the area, can we not make the DART more frequent or offer a more frequent shuttle bus out?

The Bill has the potential - I am a cautious optimist - to be a step forward for the whole country but I also believe we need to hold the NTA and all of the transport authorities to account to ensure that was is promised is delivered. I welcome the recent statements. The response back from the Oireachtas NTA-line has definitely got faster but public representatives, councillors and TDs need to have more of a say on the changes to their constituency.

On transport, I would appreciate an update on the toll bridge crossing between the northside and the southside. Can it be made contactless? Are there plans for that? It is one of the biggest bottlenecks in the city, particularly for my constituents in north Dublin who are trying to cross the Liffey. They still have to wait and pay a toll that has paid the bridge off multiple times. I know I am starting to sound like a man who normally sits here but it makes sense. We need to look into contactless payments. Clearly there is a bottleneck over the Liffey, from the northside to the southside. If we could remove that toll on that bridge, it would really speed up things in the city."""

confound_words = {"oireachtas", "éireann", "dáíl", "taoiseach", "tánaiste"}
def strip_confoundwords(text):
    return " ".join(w for w in text.split() if w.lower() not in confound_words)

result = detector.detect_multiple_languages_of(strip_confoundwords(text))


#for result in detector.detect_multiple_languages_of(strip_confoundwords(text)):
#    print(f"{result.language}: '{text[result.start_index:result.end_index]}'")

irish = sum(text.word_count for text in result if text.language == Language.IRISH)
total = sum(text.word_count for text in result)
print(f"Irish: {irish/total*100:.3f}%")

Confound_words = {"oireachtas", "éireann", "dáíl", "taoiseach", "tánaiste"}

