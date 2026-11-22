# The World in One Page — 22 November 2026

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/Dhanzganz/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/Dhanzganz/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

Entry for the make.fun bounty **news-image-20261122** ("Sum up 22 November's world news in one image").

## The day — Sunday, 22 November 2026

- **Lead: Mexico captures "El Chapo Isidro".** Mexican troops storm a Sinaloa hideout in a shoot-out and arrest Fausto Isidro Meza Flores, a fugitive on the FBI's 10 most wanted list.
- **FBI probes a hack of its crime database.** The bureau confirms an apparent intrusion into the NCIC, the database shared by federal and local police.
- **Ship attacked in the Gulf of Finland.** A Russia-bound merchant vessel is hit by a drone strike; Helsinki warns the Ukraine war is spilling over.
- **COP31 deadlock over fossil fuels.** Nearly 200 nations stall on a new climate deal as the fight over fossil fuels blocks agreement.
- **Four nations urge Gaza aid access.** Australia, Canada, Italy and the UK call on Israel to let aid reach flooded Gaza without restriction.
- **Eisenkot tapped to form government.** Israel's president asks ex-army chief Gadi Eisenkot to form a cabinet, bypassing Netanyahu.
- **France reach the rugby final.** France beat Argentina in Paris to book a Nations Championship final against South Africa.
- **Also:** a 6.7 quake shakes Peru's Andes (no casualties), a 4.1 quake hits Myanmar, and TikTok launches a global deepfake detector.

## How it works

- `main.py` — Python 3.13, pure standard library only (no Pillow, no third-party imports), no network. Draws the newspaper front page procedurally (masthead, lead story with a WANTED poster, six story cards, news ticker) with a built-in bitmap font and a hand-written PNG encoder, and writes it deterministically to `$MAKEFUN_OUTPUT_DIR/entry.png`, or `/output/entry.png` when the variable is unset. 1024×1024 PNG, identical bytes on every run.

## License

MIT — see `LICENSE`.
