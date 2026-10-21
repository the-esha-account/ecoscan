import { useState } from "react";

const TIPS = [
  "Garlic mustard stays green through winter as a low rosette, so winter is a great time to spot it.",
  "Pull garlic mustard before it sets seed in spring, and bag it. Don't compost it.",
  "English ivy stays green when everything else is bare, which makes it easy to spot on trees in winter.",
  "To free a tree from ivy, cut the vines at the base and again at chest height, then pull out the section between.",
  "Winter creeper is an evergreen vine that spreads by runners and bird-carried seeds into nearby woods.",
  "Fig buttercup is one of the first plants up in spring. It spreads by tiny tubers, so bag what you pull.",
  "Invasive shrub honeysuckles leaf out early and drop leaves late, shading out native plants beneath them.",
  "Amur and Morrow's honeysuckle have hollow stems. Snip a twig to check.",
  "Cleavers has tiny hooked bristles that catch on clothes and fur, which helps it spread.",
  "Winter is a great time to identify plants: bare trees make evergreens and invasives stand out.",
  "Pull invasives when the soil is moist, so the roots come out cleanly.",
  "Unsure if a plant is invasive? Check your state's invasive plant list or ask your local extension office.",
];

function randomIndex(exclude) {
  if (TIPS.length < 2) return 0;
  let i;
  do {
    i = Math.floor(Math.random() * TIPS.length);
  } while (i === exclude);
  return i;
}

export default function PlantTip() {
  const [index, setIndex] = useState(() => randomIndex(-1));

 return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "space-between",
      width: "100%",
      height: "100%",
      textAlign: "center"
    }}>
      <div style={{
        flex: 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 0
      }}>
        <p className="results-text" style={{ margin: 0, fontSize: "clamp(0.8rem, 2.6vw, 1rem)", lineHeight: 1.35 }}>
          {TIPS[index]}
        </p>
      </div>
      <button
        style={{ marginTop: "0.75rem", padding: "0.35rem 0.9rem", fontSize: "0.85rem" }}
        onClick={() => setIndex(randomIndex(index))}
      >
        Another tip
      </button>
    </div>
  );
}
