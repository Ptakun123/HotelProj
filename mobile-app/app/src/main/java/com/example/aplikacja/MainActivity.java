package com.example.aplikacja;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.datepicker.MaterialDatePicker;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    Button chooseDestination;
    Button chooseDate;
    String[] countries, cities;
    String chosencountry, chosencity;
    UserAndTokens userAndTokens;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Intent intent =getIntent();
        userAndTokens = intent.getExtras().getParcelable("User_data");
        TextView hello = findViewById(R.id.hello);
        chooseDestination = findViewById(R.id.chooseDestination);
        chooseDestination.setOnClickListener(this);
        chooseDate = findViewById(R.id.chooseDate);
        chooseDate.setOnClickListener(this);
        hello.setText("Witaj " + userAndTokens.getFirst_name() + " " + userAndTokens.getLast_name());
        countries = new String[]{"Polska", "Niemcy"};
        cities = new String[]{"Suwałki", "Warszawa"};
    }

    @Override
    public void onClick(View v) {
        if(v.getId() == R.id.chooseDate){ //wybieranie daty
            MaterialDatePicker.Builder<androidx.core.util.Pair<Long, Long>> builder =
                    MaterialDatePicker.Builder.dateRangePicker();

            builder.setTitleText("Wybierz zakres dat");

            MaterialDatePicker<androidx.core.util.Pair<Long, Long>> picker = builder.build();

            picker.show(getSupportFragmentManager(), "DATE_RANGE");

            picker.addOnPositiveButtonClickListener(selection -> {
                Long start = selection.first;
                Long end = selection.second;

                SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy", Locale.getDefault());
                String startStr = sdf.format(new Date(start));
                String endStr = sdf.format(new Date(end));

                Toast.makeText(this, "Wybrano: " + startStr + " – " + endStr, Toast.LENGTH_LONG).show();
                chooseDate.setText(startStr +" - " + endStr);
            });
        }
        if(v.getId() == R.id.chooseDestination){ //wybieranie miejsca
            final int[] wybrana = {-1, -1};
            new MaterialAlertDialogBuilder(this).setTitle("Wybierz kraj").setSingleChoiceItems(countries, wybrana[0], new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    wybrana[0] = which;
                }

            }) .setPositiveButton("OK", new DialogInterface.OnClickListener(){
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    if (wybrana[0] != -1) {
                        chosencountry = countries[wybrana[0]];

                        new MaterialAlertDialogBuilder(MainActivity.this).setTitle("Wybierz miasto").setSingleChoiceItems(cities, wybrana[1], new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                wybrana[0] = which;
                            }
                        }) .setPositiveButton("OK", new DialogInterface.OnClickListener(){
                                    @Override
                                    public void onClick(DialogInterface dialog, int which) {
                                        if (wybrana[0] != -1) {
                                            chosencity = cities[wybrana[0]];
                                            chooseDestination.setText(chosencountry + " " + chosencity);

                                        }
                                    }

                                }
                        ).setNegativeButton("Anuluj", null).show();
                    }
                }
            }
            ).setNegativeButton("Anuluj", null).show();
        }
    }
}

