import nltk 


debates = {
     "1" : "hello, this is a debate",
     "2" : "this is a big big debate, perhaps the biggest debate ever",
     "3" : "yes",
     "4" : "yes, too"
}




for debate in debates.values():
     count = len(debate.split())
     print(count)