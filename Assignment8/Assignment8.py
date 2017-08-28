import copy

def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    for st in states:
        V[0][st] = {"prob": start_p[st] * emit_p[st][obs[0]], "prev": None}
    # Run Viterbi when t > 0

    for t in range(1, len(obs)):
        V.append({})
        for st in states:
            max_tr_prob = max(V[t-1][prev_st]["prob"]*trans_p[prev_st][st] for prev_st in states)
            for prev_st in states:
                if V[t-1][prev_st]["prob"] * trans_p[prev_st][st] == max_tr_prob:
                    max_prob = max_tr_prob * emit_p[st][obs[t]]
                    V[t][st] = {"prob": max_prob, "prev": prev_st}
                    break
    for line in dptable(V):
        print (line)

    opt = []
    # The highest probability
    max_prob = max(value["prob"] for value in V[-1].values())
    previous = None
    # Get most probable state and its backtrack
    for st, data in V[-1].items():
        print (st, data)
        if data["prob"] == max_prob:
            opt.append(st)
            previous = st
            break
    # Follow the backtrack till the first observation
    for t in range(len(V) - 2, -1, -1):
        opt.insert(0, V[t + 1][previous]["prev"])
        previous = V[t + 1][previous]["prev"]

    print ('The steps of states are ' + ' '.join(opt) + ' with highest probability of %s' % max_prob)

def dptable(V):
     # Print a table of steps from dictionary
     yield " ".join(("%12d" % i) for i in range(len(V)))
     for state in V[0]:
         yield "%.7s: " % state + " ".join("%.7s" % ("%f" % v[state]["prob"]) for v in V)

if __name__ == "__main__":
    lines = []
    tags = {}
    temparray = []
    total_words = 0
    # read in the tags data and then format it properly
    with open("penntree.tag", "r") as sentences:
        for line in sentences:
            if (line=="\n"):
                lines.append(" ".join(temparray))
                temparray = []
            else:
                total_words += 1
                temparray.append(line.rstrip())
                tag = line.split("\t")[1].rstrip('\n')
                if tag not in tags:
                    tags[tag] = 1
                else:
                    tags[tag] += 1

    #figure out the transitions
    transitions = {key: {key2: 0 for key2 in tags} for key in tags}
    for i in lines:
        splitLine = i.split()
        lenSplitLine = len(splitLine)
        if (lenSplitLine > 3):
            prev = splitLine[1]
            j = 3
            while (j < lenSplitLine):
                transitions[prev][splitLine[j]]+=1
                prev = splitLine[j]
                j += 2
    #sanity check, should equal 270
    # print(transitions["DT"]["NN"])

    # calculate emissions for each word
    emissions = {key: {} for key in tags}
    for i in lines:
        splitLine = i.split()
        lenSplitLine = len(splitLine)
        if (lenSplitLine > 1):
            for i in range(0,lenSplitLine,2):
                word = splitLine[i]
                tag = splitLine[i+1]
                if (word in emissions[tag]):
                    emissions[tag][word] += 1
                else:
                    emissions[tag][word] = 1
    #sanity check for emissions should be 39517
    # print(emissions["the"]["DT"])

    def callViterbi(observations):
        states = list(tags)
        start_probability = {key: tags[key]/total_words for key in tags}
        transition_probability = {key: {key2: transitions[key][key2]/tags[key2] for key2 in tags} for key in tags}
        emission_probability = {tag: {word: emissions[tag][word] / tags[tag] if word in emissions[tag] else 0 for word in observations} for tag in tags}
        viterbi(observations, states, start_probability, transition_probability, emission_probability)

    #here's all the test cases from the assignment. uncomment one of the observations and then run to program to see what viterbi outputs for that sentence
    #this test should give: ‘DT, ‘VBZ,’DT’,’NN’,’.’
    # observations = ('This', 'is', 'a', 'sentence', '.')

    #this test should give 'MD', 'DT', 'NN', 'MD', 'DT', 'NN', '.'
    # If you get these outputs then your program is completely fine.First can is MD and third can is NN.Depending on the context the tags changes.
    # observations = ('Can', 'a', 'can', 'can', 'a', 'can', '?')

    # Output: 'DT', 'MD', 'VB', 'DT', 'NN', 'IN', 'DT', 'NN', 'VBZ', 'RB', '.'
    # observations = ('This', 'might', 'produce', 'a', 'result', 'if', 'the', 'system', 'works', 'well', '.')

    #Output: 'MD', 'DT', 'MD', 'VB', 'DT', 'NN', '.'
    # observations = ('Can', 'a', 'can', 'move', 'a', 'can', '?')

    #Output: 'MD', 'PRP', 'VBP', 'DT', 'NN', 'CC', 'VB', 'DT', 'NN', '.'
    # observations = ('Can', 'you', 'walk', 'the', 'walk', 'and', 'talk', 'the', 'talk', '?')

    observations = ('Can', 'you', 'say', 'how', 'a', 'can', 'can', 'run', '?')

    callViterbi(observations)
