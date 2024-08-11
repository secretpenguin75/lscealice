import matplotlib.pyplot as plt

# remove matplotlib keybord shortcuts to use our owns
if "f" in plt.rcParams["keymap.fullscreen"]:
    plt.rcParams["keymap.fullscreen"].remove("f")
if "r" in plt.rcParams["keymap.home"]:
    plt.rcParams["keymap.home"].remove("r")
if "s" in plt.rcParams["keymap.save"]:
    plt.rcParams["keymap.save"].remove("s")
if "c" in plt.rcParams["keymap.back"]:
    plt.rcParams["keymap.back"].remove("c")
if "g" in plt.rcParams["keymap.grid"]:
    plt.rcParams["keymap.grid"].remove("g")
# if 'o' in plt.rcParams['keymap.zoom']:
# plt.rcParams['keymap.zoom'].remove('o')
if "q" in plt.rcParams["keymap.quit"]:
    plt.rcParams["keymap.quit"].remove("q")
# if 'p' in plt.rcParams['keymap.pan']:
# plt.rcParams['keymap.pan'].remove('p')
if "left" in plt.rcParams["keymap.back"]:
    plt.rcParams["keymap.back"].remove("left")
if "right" in plt.rcParams["keymap.forward"]:
    plt.rcParams["keymap.forward"].remove("right")
