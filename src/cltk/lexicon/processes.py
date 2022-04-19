"""
Processes for dictionary lookup.
Extended from Clément Besnier's work by Ben Deschamps.
"""

from copy import deepcopy
from dataclasses import dataclass

from boltons.cacheutils import cachedproperty

from cltk.core.data_types import Doc, Process
from cltk.core.exceptions import CLTKException
from cltk.lexicon.lat import LatinLewisLexicon
from cltk.lexicon.non import OldNorseZoegaLexicon
from cltk.lexicon.grc import GreekLSIntLexicon

__author__ = ["Clément Besnier <clem@clementbesnier.fr>"]


@dataclass
class LexiconProcess(Process):
    """To be inherited for each language's dictionary declarations.

    Example: ``LexiconProcess`` -> ``LatinLexiconProcess``

    >>> from cltk.lexicon.processes import LexiconProcess
    >>> from cltk.lemmatize.processes import LemmatizationProcess
    >>> from cltk.core.data_types import Process
    >>> issubclass(LexiconProcess, Process)
    True
    """

    language: str = None

    @cachedproperty
    def algorithm(self):
        if self.language == "lat":
            lex_class = LatinLewisLexicon()
        elif self.language == "grc":
            lex_class = GreekLSIntLexicon()
        else:
            raise CLTKException(f"No lookup algorithm for language '{self.language}'.")
        return lex_class

    def run(self, input_doc: Doc) -> Doc:
        lookup_algo = self.algorithm
        output_doc = deepcopy(input_doc)
        for word in output_doc.words:
            if self.language == "lat":
                word.definition = lookup_algo.lookup(word.lemma)
            elif self.language == "non":
                word.definition = lookup_algo.lookup(word.string)
            elif self.language == "grc":
                word.definition = lookup_algo.lookup(word.lemma) # or should it be lemma? We don't know!
            else:
                raise CLTKException(
                    f"``LexiconProcess()`` not available for language '{self.language}' This should never happen."
                )
        return output_doc


class LatinLexiconProcess(LexiconProcess):
    """The default Latin dictionary lookup algorithm.

    >>> from cltk.lexicon.processes import LexiconProcess
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers import LatinTokenizationProcess
    >>> from cltk.lemmatize.processes import LatinLemmatizationProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Latin pipeline", \
    processes=[LatinTokenizationProcess, LatinLemmatizationProcess, LatinLexiconProcess], \
    language=get_lang("lat"))

    >>> nlp = NLP(language='lat', custom_pipeline=pipe, suppress_banner=True)
    >>> cltk_doc = nlp.analyze(text=get_example_text("lat"))
    >>> [word.definition[:10] for word in cltk_doc.words][:5]
    ['', 'est\\n\\n\\n see', 'omnis e (o', '', 'in  old in']
    """

    description = "Dictionary lookup process for Latin"
    language = "lat"

    @cachedproperty
    def algorithm(self):
        return LatinLewisLexicon()

class GreekLexiconProcess(LexiconProcess):
    # rewrite this of course
    """The default Greek dictionary lookup algorithm.

    >>> from cltk.lexicon.processes import LexiconProcess
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers import LatinTokenizationProcess #
    >>> from cltk.lemmatize.processes import LatinLemmatizationProcess #
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Latin pipeline", \
    processes=[LatinTokenizationProcess, LatinLemmatizationProcess, LatinLexiconProcess], \
    language=get_lang("lat")) #

    >>> nlp = NLP(language='grc', custom_pipeline=pipe, suppress_banner=True)
    >>> cltk_doc = nlp.analyze(text=get_example_text("lat")) #
    >>> [word.definition[:10] for word in cltk_doc.words][:5]
    ['', 'est\\n\\n\\n see', 'omnis e (o', '', 'in  old in'] #
    """

    description = "Dictionary lookup process for Greek"
    language = "grc"

    @cachedproperty
    def algorithm(self):
        return GreekLSIntLexicon()

class OldNorseLexiconProcess(LexiconProcess):
    """The default Latin dictionary lookup algorithm. #THIS COULD STAND TO BE CLEANED UP TOO

    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers import OldNorseTokenizationProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Old Norse pipeline", \
    processes=[OldNorseTokenizationProcess, OldNorseLexiconProcess], \
    language=get_lang("non"))

    >>> nlp = NLP(language='non', custom_pipeline=pipe, suppress_banner=True)
    >>> cltk_doc = nlp.analyze(text=get_example_text("non"))

    #>>> [word.definition[:10] for word in cltk_doc.words][:5] # TODO check this
    #['', '(-s, -ar),', '', 'adv.\n1) th', '']

    """

    description = "Dictionary lookup process for Old Norse"
    language = "non"

    @cachedproperty
    def algorithm(self):
        return OldNorseZoegaLexicon()
