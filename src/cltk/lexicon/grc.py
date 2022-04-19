"""Code for querying Greek language dictionaries/lexicons."""
#  Adapted from Clément Besnier's code for Latin.

import regex
import yaml

from cltk.core.exceptions import CLTKException
from cltk.data.fetch import FetchCorpus
from cltk.utils.file_operations import make_cltk_path
from cltk.utils.utils import query_yes_no

__author__ = ["Ben Deschamps <ben.deschamps@gmail.com>"]


class GreekLSIntLexicon:
    """Access a digital form of Liddell & Scott's Intermediate Greek-English Lexicon."""

    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.ml_yaml_fp = make_cltk_path(
            "grc", "lexicon", "cltk_grc_ml_lexicon", "ml.yaml"
        )
        try:
            self.entries = self._load_entries()
        except FileNotFoundError:
            if self.interactive:
                dl_msg = f"This part of the CLTK depends upon Liddell & Scott's Intermediate Greek-English Lexicon."
                print(dl_msg)
                dl_question = "Do you want to download this?"
                do_download = query_yes_no(question=dl_question)
            else:
                do_download = True
            if do_download:
                fetch_corpus = FetchCorpus(language="grc")
                fetch_corpus.import_corpus(
                    corpus_name="cltk_grc_ml_lexicon"
                )
            else:
                raise CLTKException(
                    f"File '{self.ml_yaml_fp}' is not found. It is required for this class."
                )
            self.entries = self._load_entries()

    def lookup(self, lemma: str) -> str:
        # this will need to be rewritten
        """Perform match of a lemma against headwords. If more than one match,
        then return the concatenated entries. For example:

        >>> from cltk.lexicon.grc import GreekLSIntLexicon
        >>> lll = GreekLSIntLexicon(interactive=False)
        >>> lll.lookup("clemens")[:50]
        'clēmēns entis (abl. -tī; rarely -te, L.), adj. wit'
        >>> all(word in lll.lookup("levis") for word in ["levis","lēvis"]) # Test for concatenated entries
        True
        >>> lll.lookup("omnia")
        ''
        >>> lll.lookup(".")
        ''
        >>> lll.lookup("123")
        ''
        >>> lll.lookup("175.")
        ''
        >>> lll.lookup("(") # Test for regex special character
        ''
        """
        if not self.entries:
            raise CLTKException(
                "No lexicon entries found in the .yaml file. This should never happen."
            )

        if regex.match(r"^[0-9\.\?,\:;\!\<\>\-]*$", lemma) is not None:
            return ""

        lemma = regex.escape(lemma.lower())

        keys = self.entries.keys()
        matches = [key for key in keys if regex.match(rf"^{lemma}[0-9]?$", key)]
        n_matches = len(matches)
        if n_matches > 1:
            return "\n".join([self.entries[key] for key in matches])
        elif n_matches == 1:
            return self.entries[matches[0]]
        else:
            return ""

    def _load_entries(self):
        """Read the yaml file of the lexion."""
        with open(self.ml_yaml_fp) as file_open:
            entries = yaml.load(file_open, Loader=yaml.Loader)
        return entries
