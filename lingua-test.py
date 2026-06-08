#Testing Package

from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.IRISH] #Language needs a capital - I cba
builder = LanguageDetectorBuilder.from_languages(*languages)
builder = builder.with_minimum_relative_distance(0.9)
detector = builder.build()


text = "Gabhaim buíochas leis an Aire. The reason I raised this issue is because we are coming towards the end of the school year. This will be our last opportunity at priority questions before the school year ends. At the start of the school year, school secretaries and caretakers reluctantly went on strike outside schools in pursuit of pension parity. We could all see - I hope Government could see it, and it surely knows it - the level of public support, particularly within school communities, that there is for school secretaries and caretakers. Their claim is a just one. It is for pension parity. The deep concern at this stage - and I take on board every word of the Minister's response - is that time is moving on and these individuals, in some circumstances, are making decisions about when they will retire and be able to move on. Time is of the essence."

result = detector.detect_multiple_languages_of(text)
print(result)


