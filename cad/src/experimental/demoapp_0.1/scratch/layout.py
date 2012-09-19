"""
layout.py - widget layout helpers

$Id$

"""
# semiobs:
# layout alg: leaves send min size up, extra or deficient size allocated down...
# everyone sets their min size, maybe their max size...
# in theory every size-dim has a goodness func which is piecewise linear w/ a few poss slopes...
# so children might pass up sizevars and slope, and we sort these,
# then go through the list handing out size in order of most good.
# it's pretty incremental... and with few slopes, can be summarized at levels.


# utility values of having various kinds of pixels visible
# (only order matters, I think)
##ESSENTIAL_CONTROLS_TINY = 200
ESSENTIAL_CONTROLS_NORMAL = 100
VIEWS_MINIMAL = 60
VIEWS_COMFORTABLE = 20


def desired_size_data_for_view_dimension(min_size = 10, max_size = 4000):
    "use once for each dimension"
    return desired_size_data([(VIEWS_MINIMAL, min_size), (VIEWS_COMFORTABLE, max_size - min_size)])

def desired_size_data_for_view(min_size = (10,10), max_size = (4000,4000)):
    res = [desired_size_data_for_view_dimension(min_size = min_size[i],
                                                max_size = max_size[i])
           for i in (0,1) ]
    return res

def desired_size_data_for_control(size = (20,20)):
    res = [desired_size_data([(ESSENTIAL_CONTROLS_NORMAL, size[i])])
           for i in (0,1) ]
    return res

# expect panes to maintain: size, pos; and for some kinds, min_size, max_size

def _merge_runs(data):
    res = []
    for price, number in data:
        if data and data[-1][0] == price:
            lprice, lnumber = data.pop()
            assert lprice == price # just compared
            number += lnumber
        res.append( (price, number) )
    return res

class desired_size_data(object):
    """
    how many pixels we want at each price
    """
    # self._data will be a sorted list of (price, number) pairs
    def __init__(self, price, number = None):
        if number is not None:
            assert isinstance(number, int)
            assert isinstance(price, tuple(int, float))
            self._data = [(price, number)]
        else:
            # arg1 is really a list of same format as self._data
            # fast version:
            self._data = list(price)
            self._data.sort()
            self._data.reverse() # possible optim: store negative price?
            # todo: slow version: harder to code (does all checks)
        return
    def __repr__(self):
        return "layout(%r)" % (self._data,)
    def __add__(self, other):
        # assume other is same class
        biglist = self._data + other._data
        biglist.sort()
        biglist.reverse()
        biglist = _merge_runs(biglist)
            # optim: merge the lists and compress runs, same time;
            # use an alg which can also be used to split what's available later
        return self.__class__(biglist)
    def max(self, other): # __max__ is not used, so just call it max
        # for each cumsum of pixels, what is max slope of either curve?
        def changepoints(data):
            res = {} # maps total number of pixels to
                # marginal price just as we reach it
                # (after that, price will be lower)
            total = 0
            for price, number in data:
                total += number
                res[total] = price
            return res
        cp1 = changepoints(self._data)
        cp2 = changepoints(other._data)
        bothpoints = dict(cp1)
        bothpoints.update(cp2) # values meaningless (favor cp2)
        bothpoints_items = bothpoints.items()
        bothpoints_items.sort()
        tentative = [] # (total, oldprice), but only for decreasing oldprice
        for total, oldprice in bothpoints_items:
            # oldprice favors cp2 -- let cp1 influence it too
            oldprice = max(oldprice, cp1.get(total, oldprice))
            # this is wrong, if cp1 has nothing there but something later;
            # so add to tentative, but first drop any lower or equal prices on it
            while tentative and tentative[-1][1] <= oldprice:
                del tentative[-1]
            tentative.append( (total, oldprice) )
        # now convert to desired form
        data = []
        prior_total = 0
        for total, oldprice in tentative:
            data.append( (oldprice, total - prior_total) )
            prior_total = total
                # review: more efficient to keep total??
        return self.__class__(data)
    pass

def _allocate(summands, amount):
    """
    allocate some of amount to each of the summands
    (which are desired_size_data objects)
    """ # ?
    requests = {} # maps price to list of (number, index) pairs
    for ind in range(len(summands)):
        summand = summands[ind]._data
        for price, number in summand:
            requests.setdefault(price, [])
            requests[price].append( (number, ind) )
    requests_items = requests.items()
    requests_items.sort()
    requests_items.reverse()
    results = [0] * len(summands) # added to below
    for price, pairs in requests_items:
        total = sum([number for number, index in pairs])
        if total <= amount:
            # all requests at this price can be satisfied
            for number, ind in pairs:
                results[ind] += number
            amount -= total
        else:
            # Have to divy up the remainder, among requests for various numbers
            # of pixels at the same price (and then break out of this loop).
            #
            # Note: if price curve was truly piecewise constant as our math assumes,
            # we could divy it up arbitrary, but in fact, we assume the price
            # curve is slightly convex so we should divy it up fairly.)
            #
            # Policy: hand pixels out equally until we run dry; note that some
            # requests might be smaller and fully satified, which makes the alg
            # not as simple as handing out equal shares. Also, if at the end
            # we'd hand out fractional pixels, instead we give a one-pixel
            # remainder to the first few remaining objects.
            pairs.sort() # smaller requests first
            while pairs and pairs[0][0] * len(pairs) <= amount:
                # we can fully satisfy the first request by handing out
                # the same number to everyone
                this_share = pairs[0][0]
                newpairs = []
                for number, ind in pairs:
                    results[ind] += this_share
                    amount -= this_share
                    number -= this_share
                    if number:
                        newpairs.append( (number, ind) )
                assert len(newpairs) < len(pairs) # since first one used up
                pairs = newpairs
            if amount:
                # even the first request can't be fully satisfied;
                # at this point we don't care how much the remaining ones request;
                # we just divy up the rest as equally as we can.
                assert pairs # otherwise we fully satisfied them all, so earlier test was wrong
                this_share = int( amount / len(pairs) ) # integer division desired
                for number, ind in pairs:
                    results[ind] += this_share
                    amount -= this_share
                ind = 0
                while amount:
                    results[ind] += 1
                    amount -= 1
                    ind += 1
                pass
            break
        continue
    return results

# == test code

def _test():

    lp1 = desired_size_data([(100, 3), (200, 4)])
    lp2 = desired_size_data([(100, 5), (150, 2), (250, 2)])
    print lp1
    print lp2

    print "sum, in both directions, 2 should be same:"
    # should be: [(250, 2), (200, 4), (150, 2), (100, 8)];
    # is:        [(250, 2), (200, 4), (150, 2), (100, 8)] -- correct!
    print lp1 + lp2
    print lp2 + lp1
    assert (lp1 + lp2)._data == (lp2 + lp1)._data == [(250, 2), (200, 4), (150, 2), (100, 8)]

    print "max, in both directions, 2 should be same:"
    # should be: [(250, 2), (200, 2), (100, 5)], I think;
    # is:        [(250, 2), (200, 2), (100, 5)] -- correct!
    print lp1.max(lp2)
    print lp2.max(lp1)
    assert lp1.max(lp2)._data == lp2.max(lp1)._data == [(250, 2), (200, 2), (100, 5)]
    ## print max(lp1, lp2) # this just returns a copy of lp2... not sure how it's computed... maybe by std sort order?

    print _allocate([lp1, lp2], 4) # should be: [2, 2] -- correct!
    assert _allocate([lp1, lp2], 4) == [2, 2]

    print "tests passed"

if __name__ == '__main__':
    _test()
