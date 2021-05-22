#include <bits/stdc++.h>
#include "card.h"
#include "main.h"

using namespace std;

std::vector<CardCombo> getCandidates() {
	return {};
}

inline bool gt_first(const pair<double, CardCombo> &a, const pair<double, CardCombo> &b) {
	return a.first > b.first;
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

vector<pair<double, CardCombo>> getCandidatesEval(int num) {
	vector<pair<double, CardCombo>> candidates;
	for (auto &&c : getCandidates())
		candidates.push_back({eval(c), c});
	sort(candidates.begin(), candidates.end(), gt_first);
	if (candidates.size() > num)
		candidates.resize(num);
}

int procSearch(const CardCombo &c) {
	int ans;

	if (myCards.size() == c.cards.size())
		ans = 1;
	else {
		bool is_landlord = myPosition == landlordPosition;
		auto r_lastValidCombo = lastValidCombo;
		whatTheyPlayed[myPosition].push_back(c);
		lastValidCombo = c;
		dist[myPosition] = cardSub(dist[myPosition], c);
		cardRemaining[myPosition] -= c.cards.size();
		myPosition = (myPosition + 1) % 3;
		myCards = dist[myPosition];

		ans = search();
		if (is_landlord || (myPosition == landlordPosition))
			ans = -ans;

		myPosition = (myPosition + 2) % 3;
		cardRemaining[myPosition] += c.cards.size();
		myCards = dist[myPosition] = cardAdd(dist[myPosition], c);
		whatTheyPlayed[myPosition].pop_back();
		lastValidCombo = r_lastValidCombo;
	}
	
	if (c.comboType == CardComboType::BOMB || c.comboType == CardComboType::ROCKET)
		ans *= 2;

	return ans;
}

int search() {
	static const int NUM = 3;
	auto candidates = getCandidatesEval(NUM);
	int ans = -INF;
	for (auto &&cs : candidates)
		ans = max(ans, procSearch(cs.second));
	return ans;
}

CardCombo getAction() {
	static const int DIST_NUM = 20, CAND_NUM = 10;
	auto dists = randCards(DIST_NUM);
	auto candidates = getCandidatesEval(CAND_NUM);
	for (auto &c : candidates) {
		c.first = 0;
		for (auto &&d : dists) {
			dist = d.first;
			myCards = dist[myPosition];
			c.first += d.second * procSearch(c.second);
		}
	}
	return max_element(candidates.begin(), candidates.end(), gt_first)->second;
}

double getMean() {
	static const int DIST_NUM = 20;
	auto dists = randCards(DIST_NUM);
	double ans = 0;
	for (auto &&d : dists) {
		dist = d.first;
		myCards = dist[myPosition];
		ans += d.second * search();
	}
	return ans;
}
