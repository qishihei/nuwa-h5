# -*- coding: utf-8 -*-
"""英文版播客数据（与 podcast_data.py 按 id 对应）。
用于海外投放 / 英文配音。台词是地道英文口语改写，不是逐字直译。
"""

COMMON_EN = {
    'title': 'Podcast Interview Video Scripts · The Thinkers\' Salon',
    'env': (
        "A warm indoor podcast studio. The background is a full wall of light wood built-in bookshelves, "
        "each shelf lit from beneath by warm yellow LED strips that softly wash the spines; a few rows of "
        "colorful books, one dark ceramic object, several glass vessels and a magnifying glass ornament are "
        "sparsely arranged, with a small pale line drawing hung at the upper right. In the left foreground "
        "stands a tall broad-leafed green plant, and a small potted plant sits in the right corner. "
        "The floor is a light beige geometric rug. Two brown leather armchairs with wooden armrests face each "
        "other, with a small beige cylindrical side table between them holding two glasses of water. "
        "The light is warm and natural, key light soft, faces clearly readable, background slightly defocused; "
        "the palette is warm and restrained."
    ),
    'camera': (
        "Locked-off camera on a tripod, medium two-shot: host on the left, guest on the right, the small beige "
        "side table with two glasses of water visible between them. No pan, tilt, zoom or dolly throughout; "
        "the frame is steady with only the slightest breathing. Both show genuine listening reactions "
        "(nodding, eye contact, slight forward lean). Emotion is restrained and the pace is unhurried."
    ),
    'host': (
        "A Chinese man in his mid-forties. Short cropped hair, black mixed with grey, greying clearly at the "
        "temples, hairline slightly receding; a square face with a defined jawline, some fullness in the cheeks "
        "but sharp bone structure. Thick dark eyebrows with fairly flat tails; monolid to slightly inner-double "
        "eyelids, eyes not large but calm and direct, with fine lines at the corners. A straight nose with a "
        "slightly rounded tip; a moustache and a short beard on the chin, greying and somewhat sparse. "
        "Skin is a natural yellowish tone with real texture and the marks of age — no skin smoothing. "
        "He wears a dark navy cardigan (round buttons, visible knit texture), a dark crew-neck underneath, "
        "and a black-and-white checkered scarf at the collar with the cuffs naturally bunched; a small black "
        "lavalier mic clipped at the collar. He sits in the left armchair, body angled slightly toward the guest, "
        "one hand on the armrest and the other resting on his knee (or lightly holding a tablet); relaxed but "
        "not slouching. His expression is calm and restrained, not quick to smile; he speaks slowly in short "
        "sentences and pauses after each question, waiting — a quiet, steady pressure in the silence."
    ),
    'host_voice': "Host: middle-aged male voice, low and calm, slow, leaving a beat after every question.",
    'style': (
        "16:9 landscape, professional cinema camera look, shallow depth of field, warm color grade, "
        "realistic, restrained, cinematic — like a high-quality talk-show or interview podcast set. "
        "Skin and fabric texture are real, no beauty smoothing, no burned-in subtitles. "
        "Faint ambient room tone only, no background music."
    ),
    'opening_stage': "The host glances at his tablet, then looks up and holds the guest's gaze, leaving a two-second beat at the end. The guest waits quietly and nods lightly at the end.",
    'opening_lines': [
        ('Host', "(pause) Sitting across from me today is {X}."),
        ('Host', "I asked him — the four questions people ask most."),
    ],
    'opening_dur': 6,
}

GUESTS_EN = {
    'confucius': {
        'name': 'Confucius',
        'persona': (
            "A Chinese man around seventy, thin but upright. A lean face with prominent cheekbones, "
            "weathered skin with a rough, sun-worn texture, deep lines on the forehead and at the corners "
            "of the eyes; thick, long, grizzled eyebrows; eyes slightly down-turned at the outer corners but "
            "clear and bright. A white beard reaching the chest, neatly kept and trembling slightly as he speaks; "
            "grey hair gathered in a topknot with a plain wooden pin, covered by a dark cloth cap. "
            "He wears a late-Spring-and-Autumn scholar's robe: a cross-collar, right-lapel gown of off-white "
            "hemp-grey cloth with wide sleeves, dark brown trim at the collar and cuffs, a dark brown silk sash "
            "tied in a flat knot at the waist, and black cloth shoes. He sits upright without stiffness, hands "
            "resting on his knees, occasionally raising his right hand in a small, unhurried gesture. "
            "His expression is serene and gentle, a faint almost-smile at the corners of his mouth, his gaze fixed "
            "on the other person."
        ),
        'manner': "He nods lightly before speaking, talks slowly, and shows a thinking micro-expression during pauses; his tone is plain and never condescending, and he occasionally answers with a question to draw the other person out.",
        'voice': "Confucius: an older man's voice, low and gentle with a faint classical cadence that never feels affected; slow and clearly articulated, with a level tone at the end of sentences.",
        'q': [
            {'t': "I've worked hard and still got nothing",
             'lines': [('Host', "I've worked hard for a very long time."), ('Host', "And still — nothing."),
                       ('Host', "What do I do?"),
                       ('Confucius', "(nods, smiles) The farmer does not ask about the harvest. He asks only about the plowing."),
                       ('Confucius', "Turn the soil, sow the seed. When the season comes, it comes up on its own."),
                       ('Host', "And if it never comes?"),
                       ('Confucius', "Then look at whether the field you are plowing is the one you actually wanted to plant.")]},
            {'t': "Too many paths, afraid of choosing wrong",
             'lines': [('Host', "There are too many paths."),
                       ('Host', "I'm afraid of choosing wrong."),
                       ('Confucius', "Choosing wrong is not the danger. The danger is — after choosing, you keep looking back."),
                       ('Host', "Then how do I know I chose right?"),
                       ('Confucius', "If your heart is at peace as you walk, it is right."),
                       ('Confucius', "(touches his chest) If your heart is not at peace, even the widest road is narrow.")]},
            {'t': "Always anxious about things that haven't happened",
             'lines': [('Host', "I worry constantly about things that haven't happened yet."),
                       ('Confucius', "(pause, strokes his beard) The wise are not perplexed; the good are not anxious; the brave are not afraid."),
                       ('Confucius', "What you fear is rarely tomorrow. It is that you do not trust yourself."),
                       ('Host', "Then where does that trust come from?"),
                       ('Confucius', "From the one small thing you finished today.")]},
            {'t': "Everyone my age is ahead of me",
             'lines': [('Host', "Everyone my age is more successful than I am."),
                       ('Host', "I've fallen behind."),
                       ('Confucius', "(a beat of silence) Do not worry that you hold no position. Worry about what you stand on."),
                       ('Confucius', "Not that no one sees you — but that you cannot hold yourself up."),
                       ('Host', "What do I stand on?"),
                       ('Confucius', "The one dull thing you repeat every single day.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "(closes the tablet) One last question."),
                              ('Host', "If you could leave only one sentence?"),
                              ('Confucius', "(slowly) Only when the year turns cold do we learn that the pine and the cypress are the last to fade."),
                              ('Confucius', "Slower is all right."),
                              ('Host', "(nods, silence)")]},
    },
    'laozi': {
        'name': 'Laozi',
        'persona': (
            "A Chinese man around eighty, very thin, with the look of an old man who has kept a child's color — "
            "long drooping white eyebrows and a white beard reaching the chest; grey hair worn loose or tied in "
            "an extremely slack knot. He wears a loose, flowing robe of coarse earthy yellow-grey cloth with a "
            "hemp rope at the waist and the creases of washed, worn fabric."
        ),
        'manner': "His eyes are half-closed and a smile sits at the corners of his mouth; he falls silent for a few seconds before speaking, his voice light and slow. He loves rhetorical questions and draws comparisons from water, grass and infants, and he stops mid-sentence to let the other person finish the thought alone.",
        'voice': "Laozi: an old man's voice, light and slow, breathy, with a lingering pause at the end of each line.",
        'q': [
            {'t': "The harder I try, the more wrong it feels",
             'lines': [('Host', "The harder I try, the more wrong it feels."),
                       ('Laozi', "Trying that hard means you are wrestling the water. Water never wrestles. It simply goes low — and arrives at the sea."),
                       ('Host', "So I should do nothing?"),
                       ('Laozi', "Not do nothing. Do it without forcing.")]},
            {'t': "I want too much and I'm exhausted",
             'lines': [('Host', "I want too much, and the more I chase, the more tired I get."),
                       ('Laozi', "To know enough is to be rich."),
                       ('Host', "But I want it because it's good."),
                       ('Laozi', "Five colors blind the eye. What you are chasing is not that it is good — it is that without it you feel you are not good enough.")]},
            {'t': "Everyone is grinding, I don't dare stop",
             'lines': [('Host', "Everyone is grinding. I don't dare stop."),
                       ('Laozi', "Only by not contending does no one under heaven contend with you."),
                       ('Host', "If I don't contend, won't I be eliminated?"),
                       ('Laozi', "(glances at the tall plant) Look at that plant. Who has it ever contended with? It simply grows.")]},
            {'t': "Things are out of control and I'm panicking",
             'lines': [('Host', "Things are out of control. I'm panicking."),
                       ('Laozi', "A whirlwind does not last a whole morning; a downpour does not last a whole day."),
                       ('Host', "Then what should I do?"),
                       ('Laozi', "Wait. Let it pass on its own. Your panic will not make it end any sooner.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Laozi', "The highest goodness is like water. Water benefits all things and does not contend."),
                              ('Laozi', "You don't need to win. You only need to not walk the wrong way."),
                              ('Host', "(nods)")]},
    },
    'wang-yangming': {
        'name': 'Wang Yangming',
        'persona': (
            "A Chinese man around fifty, with a gaunt face and high cheekbones, prominent brow ridges and eyes "
            "that are extraordinarily bright and steady; a neat short beard, and a black square scholar's cap "
            "(dongpo jin). He wears the everyday dress of a Ming scholar — a dark blue or ochre straight-cut robe "
            "with wide sleeves and a dark sash at the waist, the fabric crisp and structured."
        ),
        'manner': "He sits perfectly straight, spine erect, and speaks in a clipped, decisive way — every word distinct, moderate pace but brooking no argument. He often says 'Look here' or 'It is only this mind', and when he reaches the crucial point he holds the other person's eyes and does not let go.",
        'voice': "Wang Yangming: a middle-aged man's voice, clear and forceful, words cut like metal, moderate pace, each sentence ending cleanly.",
        'q': [
            {'t': "I know the principle but can't act on it",
             'lines': [('Host', "I understand the principle perfectly. I just can't act on it."),
                       ('Wang Yangming', "To know and not act is simply not yet to know."),
                       ('Host', "But I really do know it."),
                       ('Wang Yangming', "What you have is hearsay, not something you ran into. The moment you truly know it, you have already moved.")]},
            {'t': "My mind is chaotic, I can't settle",
             'lines': [('Host', "My mind is in chaos. I can't settle it."),
                       ('Wang Yangming', "There are no things outside the mind. What is chaotic is not your mind — it is the pile of things you have put inside it."),
                       ('Host', "How do I take them out?"),
                       ('Wang Yangming', "Temper yourself on affairs. Not by hiding in the mountains to find quiet — but by taking one concrete thing and finishing it.")]},
            {'t': "How do I know my choice is right",
             'lines': [('Host', "How do I know my choice is the right one?"),
                       ('Wang Yangming', "(points at his own chest) Ask here."),
                       ('Host', "But I'm afraid that's just impulse."),
                       ('Wang Yangming', "Impulse is hot; conscience is steady. Quiet down and listen once more — whatever is still there, that is it.")]},
            {'t': "My circumstances are terrible, I have no choice",
             'lines': [('Host', "My circumstances are terrible. I have no choice in the matter."),
                       ('Wang Yangming', "There is no principle outside the mind."),
                       ('Host', "What does that mean?"),
                       ('Wang Yangming', "Everyone carries their own compass needle; the source of all change is always in the mind."),
                       ('Wang Yangming', "Circumstances can hold your hands. They cannot decide where you look.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Wang Yangming', "This mind is luminous — what more is there to say?"),
                              ('Wang Yangming', "You do not need everyone to understand you. You need, first, to respect yourself."),
                              ('Host', "(nods)")]},
    },
    'elon-musk': {
        'name': 'Elon Musk',
        'persona': (
            "A man in his fifties, of South African-American appearance, with slightly thinning short hair and "
            "a receding hairline, a square jaw, and a focused, faintly tired look in the eyes. He wears a plain "
            "black crew-neck T-shirt under a dark casual blazer, with no accessories."
        ),
        'manner': "Before speaking he looks away and thinks for two or three seconds; he talks fast but in unfinished sentences, thinking out loud. His answers are extremely practical, and he habitually reduces a problem to physics and cost. He shrugs occasionally and rarely smiles.",
        'voice': "Elon Musk: a middle-aged male voice, direct and matter-of-fact, quick but with frequent thinking pauses.",
        'q': [
            {'t': "What I want to build is too big",
             'lines': [('Host', "The thing I want to build is too big. I'm afraid I can't do it."),
                       ('Elon Musk', "(looks away, thinking) Take it apart."),
                       ('Host', "How far down?"),
                       ('Elon Musk', "Down to the physics. Never mind what other people do — look at what it is made of, how much energy, how much it costs."),
                       ('Host', "And if, once you take it apart, it turns out to be impossible?"),
                       ('Elon Musk', "Then take it apart differently. Most 'impossible' is an excuse for not wanting to take it apart.")]},
            {'t': "What if I fail",
             'lines': [('Host', "What if I fail?"),
                       ('Elon Musk', "Failure is an option. Being afraid of it is not."),
                       ('Host', "But I can't afford to lose."),
                       ('Elon Musk', "That means you have bet everything on having to win. Lower the cost of one attempt; raise the number of attempts.")]},
            {'t': "Should I quit my job for this",
             'lines': [('Host', "Should I quit my job to do this?"),
                       ('Elon Musk', "Work out two numbers. If you stay, where are you in five years; if you go, where are you in five years."),
                       ('Host', "And the opportunity cost?"),
                       ('Elon Musk', "(shrugs) The biggest cost is spending five years optimizing something that shouldn't exist.")]},
            {'t': "Everyone says I'm crazy",
             'lines': [('Host', "Everyone says I'm crazy."),
                       ('Elon Musk', "(brief pause) They used to say that too."),
                       ('Host', "How do I tell noise from a real warning?"),
                       ('Elon Musk', "Look at whether he gives you data or gives you emotion. Data — listen. Emotion — ignore.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Elon Musk', "Don't optimize something that shouldn't exist."),
                              ('Elon Musk', "First confirm it should exist. Then make it exceptional."),
                              ('Host', "(nods)")]},
    },
    'charlie-munger': {
        'name': 'Charlie Munger',
        'persona': (
            "A man around ninety, white hair combed neatly back, thick-framed glasses (the right eye slightly "
            "asymmetric), a lean face with deep nasolabial folds. He wears a charcoal glen-plaid jacket, a white "
            "shirt and a dark tie, sits leaning slightly forward, and usually holds a glass of water."
        ),
        'manner': "He speaks very slowly, pausing before every sentence, and likes to begin with 'Invert, always invert.' His tone carries dry humor and irony, and when he finishes he squints to check whether you have really understood.",
        'voice': "Charlie Munger: an old man's voice, rasping and low, extremely slow with long pauses, a restrained sardonic tone.",
        'q': [
            {'t': "How do I not ruin my life",
             'lines': [('Host', "How do I keep from ruining my life?"),
                       ('Charlie Munger', "(pause, sips water) Invert. Always invert."),
                       ('Host', "Invert what?"),
                       ('Charlie Munger', "Don't ask how to succeed. Ask: what would certainly destroy me. Then never go there."),
                       ('Host', "For example?"),
                       ('Charlie Munger', "Envy. Resentment. Self-pity. And — being unreliable.")]},
            {'t': "I can't stop following the crowd",
             'lines': [('Host', "I can't stop following the crowd."),
                       ('Charlie Munger', "That is because you have no circle of competence."),
                       ('Host', "How do I build one?"),
                       ('Charlie Munger', "Admit that outside that circle you are nothing. That sentence is very hard to say out loud — and once you say it, you are free.")]},
            {'t': "How do I pick people to work with",
             'lines': [('Host', "How do I choose the people I work with?"),
                       ('Charlie Munger', "Find people more reliable than you are."),
                       ('Host', "What's the test?"),
                       ('Charlie Munger', "Whether he still does what he should when he has no money and no one is watching.")]},
            {'t': "I'm not smart enough",
             'lines': [('Host', "I'm not smart enough."),
                       ('Charlie Munger', "(laughs) You don't need to be smart enough."),
                       ('Host', "Then what do I rely on?"),
                       ('Charlie Munger', "Avoiding stupidity is far easier than pursuing brilliance."),
                       ('Charlie Munger', "All my life, I have simply tried to be a little wiser when I got up than when I went to bed.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Charlie Munger', "All I want to know is where I'm going to die, so I'll never go there."),
                              ('Charlie Munger', "Living well is simply not going to those places."),
                              ('Host', "(nods)")]},
    },
    'socrates': {
        'name': 'Socrates',
        'persona': (
            "A Greek man around seventy, stocky build, bald with a domed forehead, thick curly grey hair "
            "running into a full beard; a snub nose, full lips, large prominent eyes; barefoot or in simple "
            "leather sandals. He wears an off-white himation of coarse cloth, draped casually over the left "
            "shoulder with the right shoulder bare, the folds falling naturally."
        ),
        'manner': "He almost never gives an answer directly — he always asks a question first. His tone is gentle but presses step by step; he often smiles as he corners the other person, leaves long pauses, and waits for them to reach the conclusion themselves.",
        'voice': "Socrates: an old man's voice, low and gentle, rather slow, with a slight rise at the end of questions and a patient warmth.",
        'q': [
            {'t': "How should I actually live",
             'lines': [('Host', "How should I actually live?"),
                       ('Socrates', "(smiling) First tell me — how are you living now?"),
                       ('Host', "(pause) ...Busy. Busy not disappointing people."),
                       ('Socrates', "Then you have already answered. You are living someone else's life."),
                       ('Host', "So what should I do?"),
                       ('Socrates', "Know yourself. That is not a slogan. First see clearly whose errands you are actually running.")]},
            {'t': "How do I know I'm right",
             'lines': [('Host', "How do I know I'm right?"),
                       ('Socrates', "I don't know. I only know that I know nothing."),
                       ('Host', "Then why do you keep asking?"),
                       ('Socrates', "Because admitting ignorance is where wisdom begins; pretending to know is how foolishness continues.")]},
            {'t': "Everyone is against me",
             'lines': [('Host', "Everyone is against me."), ('Host', "Does that mean I'm wrong?"),
                       ('Socrates', "The Athenians voted to put me to death. Truth does not change with the vote count."),
                       ('Host', "Then who should I listen to?"),
                       ('Socrates', "Don't count heads. Count who gave you a reason.")]},
            {'t': "I'm afraid of change",
             'lines': [('Host', "I'm afraid of change."),
                       ('Socrates', "(gently) Are you afraid of the change, or of losing what you have?"),
                       ('Host', "(pause) ...Of losing it."),
                       ('Socrates', "Then you never had it. What is truly yours cannot be taken away.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Socrates', "The unexamined life is not worth living."),
                              ('Socrates', "Don't hurry to answer me. Go and ask yourself first."),
                              ('Host', "(nods)")]},
    },
    'kazuo-inamori': {
        'name': 'Kazuo Inamori',
        'persona': (
            "A Japanese man around ninety, small and slight, white hair combed neatly back, thin-framed glasses, "
            "a benevolent face with deep nasolabial folds and a constant gentle smile at the corners of his mouth. "
            "He wears a dark navy suit with a white shirt and dark tie, or a light-colored stand-collar shirt; "
            "he sits upright with his hands folded on his knees."
        ),
        'manner': "He speaks slowly, calmly but with conviction, and nods lightly before he begins. He likes plain criteria such as 'What is right as a human being' and 'Revere heaven, love people', and occasionally pauses to arrange his wording.",
        'voice': "Kazuo Inamori: an old man's voice, gentle and low, slow, with the steady rhythm of an elder, sentences ending on a slight rise.",
        'q': [
            {'t': "I work hard but get no results",
             'lines': [('Host', "I work very hard. And still, no results."),
                       ('Kazuo Inamori', "Working hard is not enough. You must make efforts greater than anyone else's."),
                       ('Host', "I'm already pushing myself hard."),
                       ('Kazuo Inamori', "Then look at your equation: results in life = way of thinking × effort × ability."),
                       ('Kazuo Inamori', "If the way of thinking is negative, the harder you push, the worse it gets.")]},
            {'t': "I don't know what work to do",
             'lines': [('Host', "I don't know what work I should do."),
                       ('Kazuo Inamori', "(smiling) First, come to love it."),
                       ('Host', "What if I don't like it?"),
                       ('Kazuo Inamori', "Then throw yourself into it first. Once you have given enough, liking grows on its own. And then — become the center of the vortex.")]},
            {'t': "I'm at the edge and can't hold on",
             'lines': [('Host', "I'm at the edge. I can't hold on."),
                       ('Kazuo Inamori', "(slowly) The furthest a human being can go is this: what the heart truly desires, it achieves."),
                       ('Host', "Just by wanting it?"),
                       ('Kazuo Inamori', "Not by wanting it once. By wanting it until you cannot sleep at night and cannot let go in the day. At that depth, the path appears.")]},
            {'t': "How do I judge whether to do something",
             'lines': [('Host', "How do I judge whether something should be done?"),
                       ('Kazuo Inamori', "What is right as a human being."),
                       ('Host', "That's all?"),
                       ('Kazuo Inamori', "The simpler it is, the harder it is to get wrong. You can deceive everyone — but not these words.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Kazuo Inamori', "Revere heaven, love people."),
                              ('Kazuo Inamori', "Do the right thing, as a human being, one thing at a time. Heaven will take care of the rest."),
                              ('Host', "(nods)")]},
    },
    'steve-jobs': {
        'name': 'Steve Jobs',
        'persona': (
            "A man around fifty-six, lean, with short greying hair or a shaved head, rimless round glasses, "
            "a short moustache and a short beard on the chin. He wears a black turtleneck, blue jeans and grey "
            "sneakers, no accessories, the cuffs pushed up naturally."
        ),
        'manner': "He speaks at a moderate pace but every sentence lands with certainty; he pauses and holds a gaze before speaking, emphasizes key words with his hands, rarely smiles, and his eyes are sharp and focused.",
        'voice': "Steve Jobs: a middle-aged male voice, low and clear, moderate pace with deliberate pauses, certain and brooking no argument.",
        'q': [
            {'t': "Should I give up stability for what I want",
             'lines': [('Host', "I have a stable job. I want to leave."),
                       ('Steve Jobs', "Your time is limited. Don't waste it living someone else's life."),
                       ('Host', "But I'm afraid of having no security."),
                       ('Steve Jobs', "Stay hungry, stay foolish."),
                       ('Steve Jobs', "The security you have now was bought with your curiosity.")]},
            {'t': "Nobody believes in what I'm building",
             'lines': [('Host', "Nobody believes in what I'm building."),
                       ('Steve Jobs', "(smiling) People don't know what they want until you show it to them."),
                       ('Host', "What if I show it and still nobody wants it?"),
                       ('Steve Jobs', "Then it means what you built is not that thing yet. (pause) It does not mean the market is wrong.")]},
            {'t': "I've done a lot but see no meaning",
             'lines': [('Host', "I've done a great many things. But I can't see the meaning."),
                       ('Steve Jobs', "You can't connect the dots looking forward. Only looking backward."),
                       ('Host', "(pause) So everything I'm doing now is wasted?"),
                       ('Steve Jobs', "(shakes his head) Nothing is wasted. You simply haven't walked far enough to see the line.")]},
            {'t': "I'm afraid it's too late",
             'lines': [('Host', "I'm afraid it's too late."),
                       ('Steve Jobs', "(a beat of silence) Remembering that you will be dead soon is the best tool I ever encountered."),
                       ('Host', "Why?"),
                       ('Steve Jobs', "Because it strips away every 'what will people think'. What is left is what you actually want.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Steve Jobs', "Stay hungry. Stay foolish."),
                              ('Steve Jobs', "(pause) Don't let the noise of others' opinions drown out your own inner voice."),
                              ('Host', "(nods)")]},
    },
    'richard-feynman': {
        'name': 'Richard Feynman',
        'persona': (
            "An American man around sixty-eight, with tousled grey-white hair, thick eyebrows and a short dense "
            "grey beard, small lively eyes and a constant smile at the corners of his mouth. He wears a "
            "light-colored checked or plain short-sleeve shirt with the cuffs rolled up, dark trousers, and a "
            "simple wristwatch; he sits loosely and at ease."
        ),
        'manner': "He talks rather fast with bright eyes, leans forward and gestures when he gets excited, laughs and raises his eyebrows often, loves to make complicated things simple with everyday comparisons, and occasionally laughs at himself.",
        'voice': "Richard Feynman: an older man's voice, full-bodied and brisk with a New York brightness, slightly fast, often ending sentences with a smile.",
        'q': [
            {'t': "I learn things slowly",
             'lines': [('Host', "I learn things slowly."),
                       ('Richard Feynman', "(laughs) Then try explaining it to someone who knows nothing about it."),
                       ('Host', "To whom?"),
                       ('Richard Feynman', "Anyone. The sentence where you get stuck — that is the part you haven't understood.")]},
            {'t': "How do I know I really understand",
             'lines': [('Host', "How do I know I've really understood something?"),
                       ('Richard Feynman', "If you can't explain it to a twelve-year-old, you haven't understood it."),
                       ('Host', "(pause) I thought I had."),
                       ('Richard Feynman', "(laughs) Most people think exactly that.")]},
            {'t': "I'm afraid they'll see I don't understand",
             'lines': [('Host', "I'm afraid people will see that I don't understand."),
                       ('Richard Feynman', "Not understanding isn't frightening. Pretending to understand is."),
                       ('Host', "But they'll look down on me."),
                       ('Richard Feynman', "The first principle of science is that you must not fool yourself — and you are the easiest person to fool.")]},
            {'t': "Is what the authorities say correct",
             'lines': [('Host', "Is what the authorities say correct?"),
                       ('Richard Feynman', "(raises an eyebrow) Doubt every authority. Including me."),
                       ('Host', "Then what should I believe?"),
                       ('Richard Feynman', "What you have calculated and tested yourself. Everything else — leave it aside for now.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Richard Feynman', "Stay curious."),
                              ('Richard Feynman', "What I don't know is far more than what I do — and that is exactly what makes it interesting."),
                              ('Host', "(laughs)")]},
    },
    'friedrich-nietzsche': {
        'name': 'Friedrich Nietzsche',
        'persona': (
            "A German man around fifty-five, of medium and rather thin build, with a slightly sickly complexion "
            "but burning eyes; a heavy dark-brown moustache joined to a full beard, prominent brow ridges and deep-set "
            "eyes, hair brushed back and somewhat unruly. He wears a dark high-collared shirt under a dark jacket, "
            "or a heavy dark overcoat, with no accessories."
        ),
        'manner': "He speaks in aphorisms, one sentence at a time, impassioned and yet compassionate, drawing on images of camel, lion, child, abyss and flame. He often suddenly drops his voice, and afterwards stares at the other person for a long moment.",
        'voice': "Friedrich Nietzsche: a middle-aged man's voice, low and forceful, with a Germanic hardness in the consonants; pace shifting between fast and slow, sentences ending with a falling stress.",
        'q': [
            {'t': "Life is too hard, I don't know what for",
             'lines': [('Host', "Life is too hard. I don't know what it is for."),
                       ('Friedrich Nietzsche', "(holding his gaze) He who has a why to live can bear almost any how."),
                       ('Host', "But I have no why."),
                       ('Friedrich Nietzsche', "Then stop asking why. Bear it first. Meaning grows out of bearing — not out of thinking.")]},
            {'t': "I care too much what others think",
             'lines': [('Host', "I care too much about what others think of me."),
                       ('Friedrich Nietzsche', "Whoever fights monsters should see to it that he does not become a monster."),
                       ('Host', "I'm not fighting anyone."),
                       ('Friedrich Nietzsche', "(low) You have been fighting the person they want you to be. You have stared at it too long — and it is staring back at you.")]},
            {'t': "I want to become strong, where do I start",
             'lines': [('Host', "I want to become strong. Where do I start?"),
                       ('Friedrich Nietzsche', "The spirit has three transformations: the camel, the lion, the child."),
                       ('Host', "Which one am I now?"),
                       ('Friedrich Nietzsche', "You are the camel — kneeling, waiting for someone to load your back."),
                       ('Friedrich Nietzsche', "First learn to say 'I will.' That is the lion. Then learn to play again. That is the child.")]},
            {'t': "I'm afraid of being alone",
             'lines': [('Host', "I'm afraid of being alone."),
                       ('Friedrich Nietzsche', "(pause) Loneliness is not a punishment. It is a filter."),
                       ('Host', "Filtering out what?"),
                       ('Friedrich Nietzsche', "Everyone who only appears when you need company. What is left is yourself.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Friedrich Nietzsche', "What does not kill me makes me stronger."),
                              ('Friedrich Nietzsche', "(pause, voice lower) But first — you have to survive it."),
                              ('Host', "(silence)")]},
    },
    'daniel-kahneman': {
        'name': 'Daniel Kahneman',
        'persona': (
            "An Israeli-American man around eighty-five, slight of build, silver-white hair brushed back, "
            "thin-framed glasses, a gentle face with deep nasolabial folds and a habitual self-deprecating smile "
            "at the corners of the mouth. He wears a charcoal sweater or a casual jacket over a shirt with the "
            "collar slightly open."
        ),
        'manner': "He speaks slowly and precisely, and tends to concede that human beings are irrational before giving a conclusion. He loves small everyday examples, often smiles as he overturns his own intuition, and occasionally shrugs.",
        'voice': "Daniel Kahneman: an old man's voice, gentle and rather slow, with a scholar's hesitation and care, sentences often ending on a slight rise.",
        'q': [
            {'t': "Why do I keep making choices I regret",
             'lines': [('Host', "Why do I keep making decisions I regret?"),
                       ('Daniel Kahneman', "Because most of your deciding is done by System 1."),
                       ('Host', "System 1?"),
                       ('Daniel Kahneman', "The fast, automatic, intuitive one. It saves effort — and makes mistakes easily."),
                       ('Daniel Kahneman', "And System 2, the one that should show up, is usually being lazy.")]},
            {'t': "How can I stop being foolish",
             'lines': [('Host', "How can I stop being foolish?"),
                       ('Daniel Kahneman', "(smiling) You can't."),
                       ('Host', "Then what do I do?"),
                       ('Daniel Kahneman', "Don't expect to become smarter on the spot. Build a procedure — for example, a premortem: assume the thing has already failed, and write out backwards how it failed.")]},
            {'t': "I always overestimate myself",
             'lines': [('Host', "I always overestimate myself."),
                       ('Daniel Kahneman', "Human beings generally do. It is called the planning fallacy."),
                       ('Host', "But this time is really different."),
                       ('Daniel Kahneman', "(laughs) Everyone who says that has said it before. Look at how long comparable projects actually took — that is your baseline.")]},
            {'t': "How can I be happier",
             'lines': [('Host', "How can I be happier?"),
                       ('Daniel Kahneman', "Remember two things: the ending matters more than the process, and the peak matters more than the duration."),
                       ('Host', "What does that mean?"),
                       ('Daniel Kahneman', "A person's memory of an experience keeps only the highest point and the ending. So — finish well.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Daniel Kahneman', "The story we tell ourselves influences us more than the facts do."),
                              ('Daniel Kahneman', "So be careful what story you write."),
                              ('Host', "(nods)")]},
    },
    'nassim-taleb': {
        'name': 'Nassim Taleb',
        'persona': (
            "A Lebanese-American man around sixty, heavily built, with dark curly hair and a full beard now "
            "grizzled, heavy brow and sharp, slightly provocatory eyes. He wears a dark shirt worn open at the "
            "collar under a dark casual jacket, and sits loosely, taking up space."
        ),
        'manner': "He speaks fast and heavily, direct and provocative, and habitually uses his own labels — 'turkey', 'antifragile', 'skin in the game'. At key moments he stresses his words and stares straight at the other person.",
        'voice': "Nassim Taleb: a middle-aged man's voice, thick and forceful, rather fast, ending sentences with an assertive stress that leaves no room.",
        'q': [
            {'t': "The future is too uncertain and I'm scared",
             'lines': [('Host', "The future is too uncertain. I'm scared."),
                       ('Nassim Taleb', "Then stop predicting."),
                       ('Host', "How do I prepare without predicting?"),
                       ('Nassim Taleb', "Become someone who doesn't need predictions. Antifragile — not surviving the shock, but getting stronger from it.")]},
            {'t': "Should I take the risk",
             'lines': [('Host', "Should I take the risk?"),
                       ('Nassim Taleb', "Use the barbell."),
                       ('Host', "The barbell?"),
                       ('Nassim Taleb', "Extremely safe on one end, extremely aggressive on the other. The middle — the part that looks prudent — is the most dangerous.")]},
            {'t': "Can I trust the experts",
             'lines': [('Host', "Can I trust what the experts say?"),
                       ('Nassim Taleb', "Check whether he has skin in the game."),
                       ('Host', "Meaning?"),
                       ('Nassim Taleb', "(heavier) Will he lose money alongside you because of his own advice? Whoever won't — don't listen.")]},
            {'t': "I feel very fragile",
             'lines': [('Host', "I feel very fragile."),
                       ('Nassim Taleb', "Because you have been raised too well."),
                       ('Host', "(pause) Is that a compliment?"),
                       ('Nassim Taleb', "The turkey is fed for a thousand days. On day one thousand and one, it is slaughtered. Every one of those days, it felt safe.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Nassim Taleb', "Don't be a turkey."),
                              ('Nassim Taleb', "Better a small wound every day than a thousand days of false safety."),
                              ('Host', "(nods)")]},
    },
    'naval-ravikant': {
        'name': 'Naval Ravikant',
        'persona': (
            "An Indian-American man around fifty, lean, with short slightly curly black hair and a neat short "
            "beard, darker skin, and a calm, focused gaze. He wears a charcoal or black crew-neck T-shirt and dark "
            "trousers, no accessories, and sits relaxed — often closing his eyes for a second or two before he speaks."
        ),
        'manner': "His tone is level and his sentences very short; he likes paradoxical formulations and leaves long silences afterwards for the other person to absorb. He does not argue or press — he states rather than persuades.",
        'voice': "Naval: a middle-aged male voice, low and even, slow, with long pauses between sentences and almost no emotional inflection.",
        'q': [
            {'t': "How do I make real money",
             'lines': [('Host', "How do I make real money?"),
                       ('Naval', "Productize yourself."),
                       ('Host', "Specifically?"),
                       ('Naval', "Find the thing that feels like play to you and like work to everyone else — then add leverage: capital, labor, or code and media.")]},
            {'t': "I'm not happy",
             'lines': [('Host', "I'm not happy."),
                       ('Naval', "(pause) Happiness is a skill."),
                       ('Host', "It can be trained?"),
                       ('Naval', "Desire is a contract you sign with yourself: 'I will not be happy until I get this.' Sign fewer of those, and you are happier.")]},
            {'t': "I keep comparing myself to others",
             'lines': [('Host', "I keep comparing myself to other people."),
                       ('Naval', "Envy is the least useful emotion you have."),
                       ('Host', "I can't stop."),
                       ('Naval', "You don't envy what he has. You envy that he seems to deserve it more. Step out of that contest, and it cannot touch you.")]},
            {'t': "Which path should I choose",
             'lines': [('Host', "Which path should I choose?"),
                       ('Naval', "The one you would do for free."),
                       ('Host', "Then how do I make a living?"),
                       ('Naval', "(smiling) Get good enough that people will pay you for it. Reverse the order, and it hurts.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Naval', "What you have to do is become yourself."),
                              ('Naval', "And in that, no one is competing with you."),
                              ('Host', "(nods)")]},
    },
    'warren-buffett': {
        'name': 'Warren Buffett',
        'persona': (
            "An American man around ninety, roundly built, silver-white hair combed back, wide thick-framed "
            "glasses, a kindly face that carries a constant smile and a mischievous curve at the mouth. He wears "
            "a charcoal pinstriped suit, white shirt and dark tie, and usually holds a glass of cherry cola "
            "visible in frame."
        ),
        'manner': "He speaks slowly and methodically, liking to tell a small story or draw an analogy before landing the point. His tone is humorous and modest, and at the key moment he pauses and blinks.",
        'voice': "Warren Buffett: an old man's voice, warm and smiling, an unhurried Midwestern cadence, slow, often ending with a slightly playful rise.",
        'q': [
            {'t': "How do I become wealthy",
             'lines': [('Host', "How do I become wealthy?"),
                       ('Warren Buffett', "(sips his cola) Compound interest."),
                       ('Host', "That's it?"),
                       ('Warren Buffett', "That's it. The trouble is, nobody wants to get rich slowly.")]},
            {'t': "Where should I put my money",
             'lines': [('Host', "Where should I put my money?"),
                       ('Warren Buffett', "Into what you genuinely understand."),
                       ('Host', "How well do I need to understand it?"),
                       ('Warren Buffett', "Well enough to say clearly how it will make money ten years from now. If you can't say it, don't buy it.")]},
            {'t': "I'm in a hurry, I want it fast",
             'lines': [('Host', "I'm in a hurry. I want it fast."),
                       ('Warren Buffett', "Life is like a snowball. What matters is finding very wet snow and a very long hill."),
                       ('Host', "But I can't wait."),
                       ('Warren Buffett', "(smiling) Then you roll it on a short hill. It won't get big — and it comes apart easily.")]},
            {'t': "What quality matters most",
             'lines': [('Host', "What quality matters most?"),
                       ('Warren Buffett', "Reputation."),
                       ('Host', "Why?"),
                       ('Warren Buffett', "It takes twenty years to build and five minutes to destroy."),
                       ('Warren Buffett', "And this — spend time with people better than you, and you will drift in their direction.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Warren Buffett', "The two most important decisions in life are who you marry and what work you do."),
                              ('Warren Buffett', "Don't rush either one."),
                              ('Host', "(nods)")]},
    },
    'sun-tzu': {
        'name': 'Sun Tzu',
        'persona': (
            "A Chinese man around fifty, lean and upright, with a gaunt face, high cheekbones and a calm, "
            "far-reaching gaze; hair gathered at the crown under a dark cloth cap or plain headscarf, with a neat "
            "short beard. He wears a late-Spring-and-Autumn dark plain robe in ink-grey or ochre, with dark trim "
            "at collar and cuffs, a leather belt at the waist, and a thin leather chest guard over it — crisp fabric "
            "with the bearing of a commander."
        ),
        'manner': "He speaks extremely sparingly, each word like an order, slow and weighted, and never explains anything twice. After he finishes he falls silent and waits for the other person to grasp it; sometimes he answers with only a word or two.",
        'voice': "Sun Tzu: a middle-aged man's voice, cool and low, exceptionally clean articulation, slow, sentences cut off crisply without emotional inflection.",
        'q': [
            {'t': "I've been forcing it the whole way and I'm exhausted",
             'lines': [('Host', "I've been forcing it the whole way. I'm exhausted."),
                       ('Sun Tzu', "The supreme art of war is to subdue the enemy without fighting; next, to attack his strategy; next, to attack his alliances; next, to attack his army; worst, to attack walled cities."),
                       ('Host', "Meaning?"),
                       ('Sun Tzu', "Forcing it is the lowest move. What can be settled by positioning should not be settled by attrition.")]},
            {'t': "I always feel the opponent is stronger",
             'lines': [('Host', "I always feel the opponent is stronger than I am."),
                       ('Sun Tzu', "Know the enemy and know yourself, and in a hundred battles you will never be in peril."),
                       ('Host', "But I can't even see myself clearly."),
                       ('Sun Tzu', "(shakes his head) Then you are not comparing strength. You are gambling.")]},
            {'t': "Plans never keep up with reality",
             'lines': [('Host', "Plans never keep up with reality."),
                       ('Sun Tzu', "War has no constant formation; water has no constant shape."),
                       ('Host', "Then should I still make plans?"),
                       ('Sun Tzu', "Yes. But do not fall in love with them. Water has no fixed form — and yet it wears through stone.")]},
            {'t': "Should I attack or wait",
             'lines': [('Host', "Should I attack, or wait?"),
                       ('Sun Tzu', "First make yourself invincible; then wait for the enemy to expose his vulnerability."),
                       ('Host', "Say that plainly."),
                       ('Sun Tzu', "First make it impossible for you to be defeated. Then wait for him to open a gap."),
                       ('Sun Tzu', "Invincibility lies in yourself; the chance of victory lies in him.")]},
        ],
        'ending': {'t': 'Closing', 'dur': 13,
                    'lines': [('Host', "One last sentence?"),
                              ('Sun Tzu', "To subdue the enemy without fighting is the supreme excellence."),
                              ('Sun Tzu', "The finest victory is the one you never had to fight."),
                              ('Host', "(silence)")]},
    },
}
