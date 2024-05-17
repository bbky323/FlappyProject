#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct hotel
{	char name[21];
    int level;
	double review;
	char date[9];
} HOTEL;

int main()
{	int N, i, j, C;
	HOTEL **h = NULL;
	int *num = NULL;
	double max_review;
	HOTEL max_hotel;
	int x, y;
	int cnt;
	
	scanf("%d", &N);
	h = (HOTEL **)malloc(sizeof(HOTEL *) * N);
	if (h == NULL) 
	{
		printf("Not enough memory...");
		return -1;   
	}
	
	num = (int *)malloc(sizeof(int) * N);
	if (num == NULL) 
	{
		printf("Not enough memory...");
		return -1;   
	}
	
	for (i = 0;i < N; i++)
		scanf("%d", &num[i]);
	
	for (i = 0;i < N; i++)
	{
		h[i] = (HOTEL *)malloc(sizeof(HOTEL) * num[i]);
		if (h[i] == NULL) 
	    {
			printf("Not enough memory...");
			return -1;   
	    }
		
		for (j = 0;j < num[i]; j++)
		{
			scanf("%s", h[i][j].name);
			scanf("%d", &h[i][j].level);
			scanf("%lf", &h[i][j].review);
			scanf("%s", &h[i][j].date);
		}
	}
	
	//scanf("%d %d", &x, &y);
	
	max_review = h[0][0].review;
	max_hotel = h[0][0];
	
	for (i = 0;i < N; i++)
	{
		for (j = 0;j < num[i]; j++)
		{
			if (max_review < h[i][j].review)
			{
				max_review = h[i][j].review;
				max_hotel = h[i][j];
			}
		}
	}
	
	for (i = 0;i < N;i++)
	{
		for (j = 0;j < num[i]; j++)
		{
			if (max_review == h[i][j].review)
			{
				if (strcmp(h[i][j].date, max_hotel.date) > 0)
					max_hotel = h[i][j];
			}
		}
	}	
	printf("%s %d %.1f %s\n", max_hotel.name, max_hotel.level, max_hotel.review, max_hotel.date);
	
	
	for (i = 0;i < N;i++)
		free(h[i]);
	
	free(h);
	free(num);
	
	return 0;
}