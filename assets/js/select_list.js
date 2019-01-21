function changeCodeDisplay(selectlist, switcherName) {
    var languages = [];
    for (var i in selectlist.options) {
        var language = selectlist.options[i].value;

        if (language !== undefined) {
            language = language.replace(/\s/g, '_');
            language = language.replace(/\W+/g, '');
            languages.push(language);
        }
    }

    var languageIndex = selectlist.selectedIndex;
    var selectedLanguage = languages[languageIndex];

    for (var i in languages) {
        var language = languages[i];

        var classesToSelectOn = language + '-code-block' + ' ' + switcherName;
        var languageCodeElement = document.getElementsByClassName(classesToSelectOn)[0];

        if (language == selectedLanguage) {
            languageCodeElement.classList.add("select-code-block-visible");

        }
        else {
            languageCodeElement.classList.remove("select-code-block-visible");
        }
    }
}
