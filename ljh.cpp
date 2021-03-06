#include <bits/stdc++.h>
#include "card.h"
#include "main.h"

using namespace std;

vector<CardCombo> getCandidates() {
	vector<CardCombo> r;

	auto deck = vector<Card>(myCards.begin(), myCards.end()); // 手牌
	short counts[MAX_LEVEL + 1] = {};

	unsigned short kindCount = 0;

	// 先数一下手牌里每种牌有多少个
	for (Card c : deck)
		counts[card2level(c)]++;

	// 再数一下手牌里有多少种牌
	for (short c : counts)
		if (c)
			kindCount++;

	auto addCandidate = [&](const CardCombo &pre, bool strict = 1) -> bool {
		// 然后先看一下是不是火箭，是的话就过
		CardComboType type = pre.comboType;
		if (type == CardComboType::ROCKET || type == CardComboType::BOMB)
			return 0;

		// 现在打算从手牌中凑出同牌型的牌
		// 手牌如果不够用，直接不用凑了，看看能不能炸吧
		if (deck.size() < pre.cards.size())
			return 0;

		bool fl = 0;

		// 否则不断增大当前牌组的主牌，看看能不能找到匹配的牌组
		{
			// 开始增大主牌
			int mainPackCount = pre.findMaxSeq();
			bool isSequential =
				type == CardComboType::STRAIGHT ||
				type == CardComboType::STRAIGHT2 ||
				type == CardComboType::PLANE ||
				type == CardComboType::PLANE1 ||
				type == CardComboType::PLANE2 ||
				type == CardComboType::SSHUTTLE ||
				type == CardComboType::SSHUTTLE2 ||
				type == CardComboType::SSHUTTLE4;
			for (Level i = strict ? 1 : 0;; i++) // 增大多少
			{
				for (int j = 0; j < mainPackCount; j++)
				{
					int level = pre.packs[j].level + i;

					// 各种连续牌型的主牌不能到2，非连续牌型的主牌不能到小王，单张的主牌不能超过大王
					if ((type == CardComboType::SINGLE && level > MAX_LEVEL) ||
						(isSequential && level > MAX_STRAIGHT_LEVEL) ||
						(type != CardComboType::SINGLE && !isSequential && level >= level_joker))
						return fl;

					// 如果手牌中这种牌不够，就不用继续增了
					if (counts[level] < pre.packs[j].count)
						goto next;
				}

				{
					// 找到了合适的主牌，那么从牌呢？
					// 如果手牌的种类数不够，那从牌的种类数就不够，也不行
					if (kindCount < pre.packs.size())
						continue;

					// 好终于可以了
					// 计算每种牌的要求数目吧
					short requiredCounts[MAX_LEVEL + 1] = {};
					for (int j = 0; j < mainPackCount; j++)
						requiredCounts[pre.packs[j].level + i] = pre.packs[j].count;

					function<void (unsigned, Level)> searchOthers = [&](unsigned j, Level from) {
						if (j < pre.packs.size()) {
							Level k;
							for (k = from; k <= MAX_LEVEL; k++) {
								if (requiredCounts[k] || counts[k] < pre.packs[j].count)
									continue;
								requiredCounts[k] = pre.packs[j].count;
								searchOthers(j + 1, k + 1);
								requiredCounts[k] = 0;
							}
						} else {
							// 开始产生解
							std::vector<Card> solve;
							for (Card c : deck)
							{
								Level level = card2level(c);
								if (requiredCounts[level])
								{
									solve.push_back(c);
									requiredCounts[level]--;
								}
							}
							fl = 1;
							r.push_back(CardCombo(solve.begin(), solve.end()));
							for (Card c : solve)
								requiredCounts[card2level(c)]++;
						}
					};
					searchOthers(mainPackCount, 0);
				}

			next:; // 再增大
			}
			return fl;
		}
	};

	if (lastValidCombo.comboType == CardComboType::PASS) {
		addCandidate({0}, 0);
		bool pa = addCandidate({0, 1}, 0);
		vector<Card> v;
		v = {0, 4, 8, 12};
		for (Card i = 4; i <= 11; i++) {
			v.push_back(i * 4);
			if (!addCandidate(v, 0))
				break;
		}
		if (pa) {
			v = {0, 1, 4, 5};
			for (Card i = 2; i <= 11; i++) {
				v.push_back(i * 4);
				v.push_back(i * 4 + 1);
				if (!addCandidate(v, 0))
					break;
			}

			if (addCandidate({0, 1, 2}, 0)) {
				if (addCandidate({0, 1, 2, 4}, 0))
					addCandidate({0, 1, 2, 4, 5}, 0);
				if (addCandidate({0, 1, 2, 3, 4, 8}, 0))
					addCandidate({0, 1, 2, 3, 4, 5, 8, 9}, 0);
				if (addCandidate({0, 1, 2, 4, 5, 6}, 0))
					if (addCandidate({0, 1, 2, 4, 5, 6, 8, 12}, 0))
						addCandidate({0, 1, 2, 4, 5, 6, 8, 9, 12, 13}, 0);
				if (addCandidate({0, 1, 2, 3, 4, 5, 6, 7}, 0))
					if (addCandidate({0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20}, 0))
						addCandidate({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 16, 17, 20, 21}, 0);
			}
		}
	} else {
		r.push_back(CardCombo());
		addCandidate(lastValidCombo);
	}
	// 实在找不到啊
	// 最后看一下能不能炸吧

	if (lastValidCombo.comboType != CardComboType::ROCKET) {
		for (Level i = 0; i < level_joker; i++)
			if (counts[i] == 4 && (lastValidCombo.comboType != CardComboType::BOMB || i > lastValidCombo.packs[0].level)) // 如果对方是炸弹，能炸的过才行
			{
				// 还真可以啊……
				Card bomb[] = {Card(i * 4), Card(i * 4 + 1), Card(i * 4 + 2), Card(i * 4 + 3)};
				r.push_back(CardCombo(bomb, bomb + 4));
			}
	}

	// 有没有火箭？
	if (counts[level_joker] + counts[level_JOKER] == 2)
	{
		Card rocket[] = {card_joker, card_JOKER};
		r.push_back(CardCombo(rocket, rocket + 2));
	}

	// ……
	return r;
}

inline bool gt_first(const pair<double, CardCombo> &a, const pair<double, CardCombo> &b) {
	return a.first > b.first;
}

inline bool le_first(const pair<double, CardCombo> &a, const pair<double, CardCombo> &b) {
	return a.first < b.first;
}

constexpr int INF = 0x3f3f3f3f;

CardSet cardSub(const CardSet &s, const CardCombo &c) {
	CardSet r = s;
	for (Card v : c.cards)
		r.erase(v);
	return r;
}

CardSet cardAdd(const CardSet &s, const CardCombo &c) {
	CardSet r = s;
	for (Card v : c.cards)
		r.insert(v);
	return r;
}

vector<pair<double, CardCombo>> getCandidatesEval(int num, bool worstCase) {
	vector<pair<double, CardCombo>> candidates;
	double s = 0.0;
	for (auto &&c : getCandidates()) {
		double v = exp(eval(c, worstCase));
		candidates.push_back({v, c});
		s += v;
	}
	for (auto &c : candidates)
		c.first /= s;
	sort(candidates.begin(), candidates.end(), gt_first);
	if (num != -1 && candidates.size() > num)
		candidates.resize(num);
	return candidates;
}

int getMaxSc() {
	static int Num[MAX_LEVEL];
	memset(Num, 0, sizeof(Num));
	for (Card c : dist[myRealPosition])
		Num[card2level(c)]++;
	int ans = 1;
	for (int i = 0; i < MAX_LEVEL; i++)
		if (Num[i] == 4)
			ans <<= 1;
	if (Num[level_joker] && Num[level_JOKER])
		ans <<= 1;
	return ans;
}

double getCandidateProb(const CardCombo &c) {
	auto candidates = getCandidatesEval(-1, 1); // worstCase
	for (auto &&p : candidates)
		if (p.second == c)
			return p.first;
	return 0.0;
}

void doCombo(const CardCombo &c) {
	whatTheyPlayed[myPosition].push_back(c);
	if (c.comboType != CardComboType::PASS) {
		lastValidCombo = c;
		lastValidComboPosition = myPosition;
	} else if (lastValidComboPosition == (myPosition + 1) % PLAYER_COUNT) {
		lastValidCombo = CardCombo();
		lastValidComboPosition = -1;
	}
	dist[myPosition] = cardSub(dist[myPosition], c);
	cardRemaining[myPosition] -= c.cards.size();
	myPosition = (myPosition + 1) % PLAYER_COUNT;
	myCards = dist[myPosition];
}

void undoCombo() {
	myPosition = (myPosition + PLAYER_COUNT - 1) % PLAYER_COUNT;
	const CardCombo &c = whatTheyPlayed[myPosition].back();
	cardRemaining[myPosition] += c.cards.size();
	myCards = dist[myPosition] = cardAdd(dist[myPosition], c);
	whatTheyPlayed[myPosition].pop_back();
	lastValidCombo = CardCombo();
	lastValidComboPosition = -1;
	for (int p = 1; p < PLAYER_COUNT; p++) {
		int pos = (myPosition + PLAYER_COUNT - p) % PLAYER_COUNT;
		const auto &v = whatTheyPlayed[pos];
		if (v.empty())
			break;
		const auto &d = v.back();
		if (d.comboType != CardComboType::PASS) {
			lastValidCombo = d;
			lastValidComboPosition = pos;
			break;
		}
	}
}

int procSearch(const CardCombo &c) {
	int ans;

	if (myCards.size() == c.cards.size())
		ans = 1;
	else {
		bool is_landlord = myPosition == landlordPosition;

		doCombo(c);
		ans = search();
		if (is_landlord || (myPosition == landlordPosition))
			ans = -ans;
		undoCombo();
	}
	
	if (myPosition == myRealPosition && (c.comboType == CardComboType::BOMB || c.comboType == CardComboType::ROCKET))
		ans *= 2;

	return ans;
}

bool termFlag = 0;

int search() {
	static int cnt = 0;
	int num = 4;
	if (myCards.size() > 3)
		num = 2;
	if (myCards.size() > 6)
		num = 1;
	int maxSc = getMaxSc();
	auto candidates = getCandidatesEval(num);
	int ans = -INF;
	for (auto &&cs : candidates) {
		ans = max(ans, procSearch(cs.second));
#ifndef _DEBUG
		if (termFlag || (((++cnt) & 1023) == 0 && clock() > 0.9 * CLOCKS_PER_SEC)) {
#ifdef _LOG
			if (!termFlag)
				cerr << "TERM" << endl;
#endif
			termFlag = 1;
			return ans;
		}
#endif
		if (ans == maxSc)
			break;
	}
	return ans;
}

CardCombo getAction() {
	static const int DIST_NUM = 100, CAND_NUM = 10, THRESHOLD = 8, THRESHOLD_OTHERS = 2;

	if (myCards.size() > THRESHOLD && *min_element(cardRemaining, cardRemaining + PLAYER_COUNT) > THRESHOLD_OTHERS) {
		dist = randCards(1, 0.5)[0].first;
		myCards = dist[myPosition];
		auto candidates = getCandidatesEval(-1, 1); // worstCase
#ifdef _LOG
		cerr << "Candidates:" << endl;
		for (auto &&c : candidates) {
			cerr << c.first << endl;
			for (Card v : c.second.cards)
				cerr << v << ' ';
			cerr << endl;
			cerr << "----------" << endl;
		}
#endif
		return candidates[0].second;
	}
	auto dists = randCards(DIST_NUM, 0.1);
#ifdef _LOG
	cerr << "Rand Time: " << (double)clock() / CLOCKS_PER_SEC << endl;
#endif
	dist = dists[0].first;
	myCards = dist[myPosition];
	auto candidates = getCandidatesEval(CAND_NUM);
#ifdef _LOG
	cerr << "Dist Prob:" << endl;
	for (auto &&d : dists) {
		// for(auto i:d.first[0])cerr<<card2level(i)<<" "; puts(""); 
		cerr << d.second << endl;
	}
	cerr << "Candidates:" << endl;
#endif
	for (auto &c : candidates) {
#ifdef _LOG
		cerr << c.first << endl;
		for (Card v : c.second.cards)
			cerr << v << ' ';
		cerr << endl;
		cerr << "----------" << endl;
#endif
		c.first *= 0.03*cardRemaining[myPosition];
		
	}
	int debug = 0;
	for (auto &&d : dists) {
		dist = d.first;
		myCards = dist[myPosition];
		for (auto &c : candidates) {
			debug++;
			int r = procSearch(c.second);
#ifdef _LOG
			// cerr << r << endl;
#endif
			c.first += d.second * r;
			if (termFlag)
				break;
		}
		if (termFlag)
			break;
	}
#ifdef _LOG
	cerr << "Candidates Res:" << endl;
	for (auto &c : candidates)
		cerr << c.first << endl;
#endif
	return max_element(candidates.begin(), candidates.end(), le_first)->second;
}

/*
double getMean() {
	static const int DIST_NUM = 20;
	auto dists = randCards(DIST_NUM, 0.1);
	double ans = 0;
	for (auto &&d : dists) {
		dist = d.first;
		myCards = dist[myPosition];
		ans += d.second * search();
	}
	return ans;
}
*/
