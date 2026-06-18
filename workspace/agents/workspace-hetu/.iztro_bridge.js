const { astro } = require('/home/openclaw/.npm-global/lib/node_modules/iztro');

function toTimeIndex(hour, minute) {
    const shichen = [
        [23, 1, 0], [1, 3, 1], [3, 5, 2], [5, 7, 3],
        [7, 9, 4], [9, 11, 5], [11, 13, 6], [13, 15, 7],
        [15, 17, 8], [17, 19, 9], [19, 21, 10], [21, 23, 11],
    ];
    for (const [start, end, idx] of shichen) {
        if (hour >= start && hour < end) return idx;
        if (start === 23 && (hour >= 23 || hour < 1)) return 0;
    }
    return Math.floor(hour / 2) % 12;
}

// 从 stdin 读取参数
const raw = require('fs').readFileSync('/dev/stdin', 'utf8').trim();
const args = JSON.parse(raw);
const hour = args.hour;
const minute = args.minute;
const timeIndex = toTimeIndex(hour, minute);

const star = astro.bySolar(args.date, timeIndex, args.gender);

const result = {
    bazi: star.chineseDate,
    gender: star.gender,
    lunarDate: star.lunarDate,
    solarDate: star.solarDate,
    time: star.time,
    timeRange: star.timeRange,
    zodiac: star.zodiac,
    sign: star.sign,
    fiveElementsClass: star.fiveElementsClass,
    soul: star.soul,
    body: star.body,
    soulBranch: star.earthlyBranchOfSoulPalace,
    bodyBranch: star.earthlyBranchOfBodyPalace,
    palaces: star.palaces.map(p => ({
        index: p.index,
        name: p.name,
        earthlyBranch: p.earthlyBranch,
        heavenlyStem: p.heavenlyStem,
        majorStars: (p.majorStars || []).map(s => ({
            name: s.name, type: s.type, brightness: s.brightness || '', mutagen: s.mutagen || ''
        })),
        minorStars: (p.minorStars || []).map(s => ({
            name: s.name, type: s.type, brightness: '', mutagen: ''
        })),
        adjStars: (p.adjectiveStars || []).map(s => ({
            name: s.name, type: s.type, brightness: '', mutagen: ''
        })),
        changsheng12: p.changsheng12 || '',
        boshi12: p.boshi12 || '',
        jiangqian12: p.jiangqian12 || '',
        suiqian12: p.suiqian12 || '',
        decadal: p.decadal,
        ages: p.ages || []
    })),
    transformations: []
};

for (const p of star.palaces) {
    for (const s of (p.majorStars || [])) {
        if (s.mutagen) {
            result.transformations.push({
                palace: p.name,
                star: s.name,
                mutagen: s.mutagen
            });
        }
    }
}

console.log(JSON.stringify(result));
