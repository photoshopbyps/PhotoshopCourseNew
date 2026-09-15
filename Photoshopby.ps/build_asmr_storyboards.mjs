import { mkdirSync, writeFileSync } from 'node:fs';

const scenes = [
  ['S01','Clean hero arrangement; both gloved hands place the subject at the center mark.','Wide establish, 45-degree front'],
  ['S02','Left hand steadies the subject; right hand sets the knife parallel to the cutting line.','Top-down macro'],
  ['S03','The blade edge touches without cutting; reflections and material texture are introduced.','Extreme close-up, side profile'],
  ['S04','Right hand tests a tiny, controlled tap on the surface; no object displacement.','POV close-up'],
  ['S05','Knife lifts 3 cm, keeping the blade square to the subject.','Macro 3/4 angle'],
  ['S06','First shallow score begins at the near edge; left fingers remain outside blade path.','Top-down close-up'],
  ['S07','The score travels one third across in one smooth, slow stroke.','Side macro tracking'],
  ['S08','The score reaches the center; loose micro-particles remain on the mat.','Extreme close-up'],
  ['S09','The score finishes at the far edge; knife exits in the same direction.','Top-down close-up'],
  ['S10','Hands pause; blade is set beside the score while the object remains aligned.','Overhead still'],
  ['S11','A thin wedge/guide is positioned in the score with tweezers.','Macro 45-degree'],
  ['S12','Guide is pressed evenly; the material begins to show a controlled separation line.','Extreme close-up, side'],
  ['S13','Right hand removes the guide and returns to the original knife grip.','POV close-up'],
  ['S14','Second cut starts from the near edge, perpendicular to the first score.','Top-down macro'],
  ['S15','Blade advances slowly; hand pressure stays gentle and centred.','Macro side tracking'],
  ['S16','Second cut crosses the first at the exact center.','Extreme close-up, top-down'],
  ['S17','Second cut completes at the far edge; pieces remain in their original outline.','Top-down close-up'],
  ['S18','Knife is lifted vertically and placed on the magnetic rest.','Close-up, 45-degree'],
  ['S19','Both hands apply balanced outward pressure at the scored edges.','Top-down macro'],
  ['S20','The first clean segment releases; particles fall naturally onto the dark mat.','Ultra macro, side'],
  ['S21','Segment is nudged 2 cm aside with a silicone-tipped tool.','Top-down close-up'],
  ['S22','The remaining piece is rotated exactly 90 degrees, keeping the center mark visible.','Overhead close-up'],
  ['S23','Knife returns; third controlled score begins on the rotated face.','Macro 3/4 angle'],
  ['S24','Third score deepens in a single continuous pass.','Side macro tracking'],
  ['S25','Hands pause to show the crisp line and intact surrounding material.','Extreme close-up'],
  ['S26','A narrow chisel/wedge follows the score with a gentle press.','POV macro'],
  ['S27','A second segment releases with physically plausible resistance.','Ultra macro, side'],
  ['S28','Tweezers arrange the segments in a tidy fan, without changing the tabletop setup.','Top-down close-up'],
  ['S29','Knife makes one final small finishing cut on the largest remaining segment.','Macro side profile'],
  ['S30','Final small segment separates and settles; no jump in particle placement.','Extreme close-up, slow motion'],
  ['S31','Completed pieces are aligned as a symmetrical ASMR display; tools stay at frame right.','Top-down hero shot'],
  ['S32','Hands leave frame; a slow light sweep reveals the finished texture and clean workspace.','Locked-off macro hero']
];

const clips = [
  ['01','Glass_Strawberry','glass fruit','a translucent ruby-red glass strawberry with tiny raised seeds'],
  ['02','Glass_Orange','glass fruit','a translucent amber glass orange with segmented interior detail'],
  ['03','Glass_Kiwi','glass fruit','a translucent emerald glass kiwi with pale radial core and black seeds'],
  ['04','Glass_Watermelon','glass fruit','a translucent pink-and-green glass watermelon wedge with dark seeds'],
  ['05','Glass_Grape','glass fruit','a translucent violet glass grape cluster, cut one grape at a time'],
  ['06','Hard_Gold_Bar','hard gold','a dense 24-karat gold bar with engraved serial number and brushed faces'],
  ['07','Hard_Gold_Ingot','hard gold','a compact cast gold ingot with rounded corners and fine casting texture'],
  ['08','Hard_Gold_Coin_Stack','hard gold','a stack of thick solid gold coins with reeded edges, handled as one aligned stack'],
  ['09','Hard_Gold_Prism','hard gold','a polished rectangular hard-gold prism with beveled edges'],
  ['10','Hard_Gold_Nugget','hard gold','a refined hard-gold nugget with faceted, mineral-like surface']
];

function subjectAction(kind, action) {
  if (kind === 'glass fruit') return action.replaceAll('material', 'glass').replace('particles', 'tiny glass chips');
  return action.replaceAll('knife', 'diamond-edged precision cutting tool').replaceAll('material', 'gold').replace('particles', 'fine gold dust');
}
function videoPrompt(id, action, kind) {
  const pace = id === 'S20' || id === 'S27' || id === 'S30' ? 'Capture the release at 120 fps, then play back in delicate slow motion.' : 'Move at a measured ASMR pace over 0.35 seconds.';
  const physics = kind === 'glass fruit' ? 'Glass chips obey gravity with subtle sparkle; no rubbery deformation.' : 'Dense gold moves with weight and slight friction; dust settles naturally.';
  return `${pace} ${action} Preserve the exact hand position, tabletop layout, and key light from the prior shot. ${physics} No camera shake, morphing, extra fingers, text changes, or scene cuts.`;
}

const production = {
  project: 'ASMR Precision Cutting — Glass Fruit & Hard Gold',
  delivery: { clips: 10, scenesPerClip: 32, totalImages: 320, status: '[320/320 images ready as storyboard specifications]', targetDuration: '10–15 seconds per clip', suggestedFrameDuration: '0.31–0.47 seconds per scene' },
  globalContinuity: {
    operator: 'same anonymous craftsperson; clean matte-black nitrile gloves; only hands and forearms visible',
    set: 'matte charcoal cutting mat, black slate workbench, stainless magnetic tool rest at frame right, no logos',
    lighting: 'single soft 5600K key from upper left, subtle cool fill, dark controlled background, consistent exposure',
    safetyAndReality: 'Fictional luxury-ASMR treatment. Use a diamond-edged precision tool and restrained hand pressure; do not depict unsafe force, implausible melting, or impossible deformation.'
  },
  clips: clips.map(([number, title, kind, subject]) => ({
    clipId: `Clip_${number}_${title}`,
    title: title.replaceAll('_',' '),
    context: kind === 'glass fruit' ? 'Studio glass-fruit precision cutting on a charcoal mat' : 'Studio hard-gold precision cutting on a charcoal mat',
    status: '[32/32]',
    folder: `Clip_${number}_${title}/`,
    scenes: scenes.map(([id, baseAction, camera]) => {
      const action = subjectAction(kind, baseAction);
      const shotType = camera.toLowerCase().replaceAll(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      return {
        sceneId: id,
        actionAndContinuity: `${action} Subject: ${subject}. Continuity: same black gloves, charcoal mat, tool rest at right, and 5600K upper-left key light.`,
        cameraShot: camera,
        imageFile: `${id}_${shotType}.png`,
        imagePrompt: `Photorealistic high-resolution ASMR product-craft still, ${camera.toLowerCase()}, ${subject}, ${action.toLowerCase()}. Same anonymous craftsperson in matte-black nitrile gloves, matte charcoal cutting mat, black slate workbench, stainless magnetic tool rest at frame right; soft 5600K key light from upper left, subtle cool fill, controlled dark background, micro-surface detail, physically accurate reflections, shallow depth of field, 16:9, no face, no logo, no text overlay.`,
        videoGenPrompt: videoPrompt(id, action, kind)
      };
    })
  }))
};

mkdirSync('ASMR_Precision_Cutting_Package', { recursive: true });
for (const clip of production.clips) mkdirSync(`ASMR_Precision_Cutting_Package/${clip.folder}`, { recursive: true });
writeFileSync('ASMR_Precision_Cutting_Package/storyboard_index.json', JSON.stringify(production, null, 2) + '\n');
writeFileSync('ASMR_Precision_Cutting_Package/README.md', `# ${production.project}\n\n${production.delivery.status}\n\nEach clip folder is ready for S01–S32 image assets; all scene metadata and English image/video prompts are in \`storyboard_index.json\`.\n`);
