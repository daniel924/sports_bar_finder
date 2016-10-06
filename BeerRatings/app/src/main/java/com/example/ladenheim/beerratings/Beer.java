package com.example.ladenheim.beerratings;

/**
 * Created by ladenheim on 10/3/16.
 */
public class Beer {
    String name;
    Double ratingBeerAdvocate;
    Double ratingUntappd;

    public Beer(String name, Double ratingBeerAdvocate, Double ratingUntappd) {
        this.name = name;
        this.ratingBeerAdvocate = ratingBeerAdvocate;
        this.ratingUntappd = ratingUntappd;
    }
}
